from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from django.test import Client, TestCase

from spaces.models import Space, Document, Revision


class RevisionViewTest(TestCase):

    def setUp(self):
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
        Revision.objects.create(
            content='Second version',
            author=self.author,
            doc=self.doc)

    def test_correct_revisions_is_shown(self):
        response = self.client.get(
            reverse('spaces:document', args=('mine/foo',)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Second version")

    def test_authed_user_is_author(self):
        # response = self.client.post(
        #     reverse('spaces:document_create', args=('mine/foo',)))
        pass

    def test_spoof_author_user(self):
        pass
