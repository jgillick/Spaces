from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import Client, RequestFactory, TestCase

from spaces.models import Space, Document, Revision
from spaces import views


class RevisionViewTest(TestCase):

    def setUp(self):
        self.factory = RequestFactory()

        self.space = Space.objects.create(name='My Space!', path='mine')

        # Users
        self.author = get_user_model().objects.create_user(
            username='bob',
            email='bob@dobbs.com',
            password='noneofyourbusiness')
        self.other_user = get_user_model().objects.create_user(
            username='john',
            email='john@doe.com',
            password='noneofyourbusiness')

        # Document and two revisions
        self.doc = Document.objects.create(
            title='Foo',
            path='foo',
            space=self.space)
        Revision.objects.create(
            content='First version',
            author=self.author,
            doc=self.doc)
        rev = Revision.objects.create(
            content='Second version',
            author=self.author,
            doc=self.doc)

        self.other_doc = Document.objects.create(
            title='Other',
            path='other',
            space=self.space)

        self.test_data = {
            'title': 'hello',
            'path': 'foo',
            'revision_set-TOTAL_FORMS': 1,
            'revision_set-INITIAL_FORMS': 1,
            'revision_set-MIN_NUM_FORMS': 1,
            'revision_set-MAX_NUM_FORMS': 1,
            'revision_set-0-content': 'hello world',
            'revision_set-0-id': rev.id,
            'revision_set-0-doc': self.doc.id
        }

    def post_update(self, path, data):
        """ Send an document edit POST request. """
        request = self.factory.post(
            reverse('spaces:document_create', kwargs={"path": path}),
            data)
        request.user = self.author
        return views.DocUpdate.as_view()(request, path=path)

    def test_correct_revisions_is_shown(self):
        """ The latest revision should be shown for a document. """
        response = self.client.get(
            reverse('spaces:document', args=('mine/foo',)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Second version")

    def test_auth_required_to_create(self):
        """ Only authenticated users can create a document. """
        response = self.client.get(
            reverse('spaces:document_create', kwargs={"path": "mine/foo/"}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith(settings.LOGIN_URL))

        response = self.client.post(
            reverse('spaces:document_create', kwargs={"path": "mine/foo/"}),
            self.test_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith(settings.LOGIN_URL))

    def test_auth_required_to_edit(self):
        """ Only authenticated users can edit a document. """
        response = self.client.get(
            reverse('spaces:document_edit', kwargs={"path": "mine/foo/"}))

        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith(settings.LOGIN_URL))

    def test_spoof_author_user(self):
        """ Should not be able to spoof the author. """
        self.test_data["revision_set-0-author"] = self.other_user.id

        response = self.post_update("mine/foo/", self.test_data)
        rev = Revision.objects.last()
        self.assertEqual(rev.author.id, self.author.id)

    def test_duplicate_path(self):
        """ Cannot create a document with an existing path. """
        self.client.login(username="bob", password="noneofyourbusiness")
        response = self.client.post(
            reverse('spaces:document_create', kwargs={"path": "mine/foo/"}),
            self.test_data)

        self.assertFormError(
            response, "form", "path", "This path already exists")
