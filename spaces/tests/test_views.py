from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group, Permission
from django.core.urlresolvers import reverse
from django.test import Client, override_settings, RequestFactory, TestCase

from spaces.models import AccessLog, Space, Document, Revision
from spaces import views
from spaces.conf import merge_settings


@override_settings(
    SPACES_AUTH_GUEST_CAN_VIEW=True,
    SPACES_AUTH_ANY_USER_CAN_EDIT=True)
class RevisionViewTest(TestCase):

    def setUp(self):
        merge_settings()
        self.factory = RequestFactory()

        self.space = Space.objects.create(name='My Space!', path='mine')

        # Users
        self.author = get_user_model().objects.create_user(
            username='bob',
            email='bob@dobbs.com',
            password='password')
        self.other_user = get_user_model().objects.create_user(
            username='john',
            email='john@doe.com',
            password='password')

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
        return views.DocUpdateView.as_view()(request, path=path)

    def test_correct_revisions_is_shown(self):
        """ The latest revision should be shown for a document. """
        response = self.client.get(
            reverse('spaces:document', args=('mine/foo',)))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Second version")

    def test_spoof_author_user(self):
        """ Should not be able to spoof the author. """
        self.test_data["revision_set-0-author"] = self.other_user.id

        response = self.post_update("mine/foo/", self.test_data)
        rev = Revision.objects.last()
        self.assertEqual(rev.author.id, self.author.id)

    def test_duplicate_path(self):
        """ Cannot create a document with an existing path. """
        self.client.login(username="bob", password="password")
        response = self.client.post(
            reverse('spaces:document_create', kwargs={"path": "mine/foo/"}),
            self.test_data)

        self.assertFormError(
            response, "form", "path", "This path already exists")

    def test_access_log(self):
        """ An access log should be generated for every document view """
        self.client.login(username="bob", password="password")
        self.client.get(
            reverse('spaces:document', args=('mine/foo',)))

        logs = AccessLog.objects.all()
        self.assertEqual(logs.count(), 1)
        self.assertEqual(logs[0].user.username, 'bob')
        self.assertEqual(logs[0].document.path, 'foo')


class AuthenticatedViewsTest(TestCase):

    """ Test various authentication cases. """

    def setUp(self):

        # Create users
        self.basic_user = get_user_model().objects.create_user(
            username='basic',
            email='basic@basic.com',
            password='password')
        self.viewer_user = get_user_model().objects.create_user(
            username='viewer',
            email='viewer@viewer.com',
            password='password')
        self.editor_user = get_user_model().objects.create_user(
            username='editor',
            email='editor@editor.com',
            password='password')

        # Viewer permissions
        for p in ['view_document', 'view_space']:
            self.viewer_user.user_permissions.add(
                Permission.objects.get(codename=p))

        # Editor permissions
        for p in ['add_document', 'change_document', 'delete_document',
                  'add_revision', 'change_revision', 'delete_revision']:
            self.editor_user.user_permissions.add(
                Permission.objects.get(codename=p))

        # Initial docs
        self.space = Space.objects.create(name='My Space!', path='mine')
        self.doc = Document.objects.create(
            title='Foo',
            path='foo',
            space=self.space)
        Revision.objects.create(
            content='First version',
            author=self.editor_user,
            doc=self.doc)

        # URLs
        self.view_url = reverse('spaces:document',
                                kwargs={"path": "mine/foo"})
        self.create_url = reverse('spaces:document_create',
                                  kwargs={"path": "mine/new"})
        self.edit_url = reverse('spaces:document_edit',
                                kwargs={"path": "mine/foo"})
        self.delete_url = reverse('spaces:document_delete',
                                  kwargs={"pk": self.doc.pk})

    def assert_auth_redirect(self, response):
        """ Check if response is a auth redirect. """
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response['location'].startswith(settings.LOGIN_URL))

    def failing_edit_tests(self):
        response = self.client.get(self.create_url)
        self.assert_auth_redirect(response)
        response = self.client.post(self.delete_url)
        self.assert_auth_redirect(response)
        response = self.client.post(self.delete_url)
        self.assert_auth_redirect(response)

    def passing_edit_tests(self):
        # Create
        response = self.client.get(self.create_url)
        self.assertEqual(response.status_code, 200)

        # Edit
        response = self.client.get(self.edit_url)
        self.assertEqual(response.status_code, 200)

        # Delete
        response = self.client.post(self.delete_url)
        self.assertEqual(response.status_code, 302)
        self.assertFalse(
            response['location'].startswith(settings.LOGIN_URL))

    def test_guest_cannot_view(self):
        """
        Guest users cannot view when SPACES_AUTH_GUEST_CAN_VIEW is False.
        """
        with self.settings(SPACES_AUTH_GUEST_CAN_VIEW=False):
            merge_settings()

            response = self.client.get(self.view_url)
            self.assert_auth_redirect(response)

    def test_view_users_access(self):
        """
        User's with view permissions can view when SPACES_AUTH_GUEST_CAN_VIEW
        is False.
        """
        with self.settings(SPACES_AUTH_GUEST_CAN_VIEW=False):
            merge_settings()

            self.client.login(username="viewer", password="password")
            response = self.client.get(self.view_url)

            self.assertEqual(response.status_code, 200)

    def test_login_to_edit(self):
        """ Only authenticated users can edit documents. """
        response = self.client.get(self.create_url)
        self.assert_auth_redirect(response)

        response = self.client.get(self.edit_url)
        self.assert_auth_redirect(response)

    def test_any_user_can_edit(self):
        """
        Any authenticated user can edit when SPACES_AUTH_ANY_USER_CAN_EDIT
        is False.
        """
        with self.settings(SPACES_AUTH_ANY_USER_CAN_EDIT=True):
            merge_settings()

            # Anon user not allowed
            self.failing_edit_tests()

            # After auth, should be able to create/edit
            self.client.login(username="viewer", password="password")
            self.passing_edit_tests()

    def test_only_edit_users_can_edit(self):
        """
        Only user's with edit permissions can edit documents when
        SPACES_AUTH_ANY_USER_CAN_EDIT is False.
        """
        with self.settings(SPACES_AUTH_ANY_USER_CAN_EDIT=False):
            merge_settings()

            # Basic user not allowed
            self.client.login(username="basic", password="password")
            self.failing_edit_tests()

            # Editor user allowed
            self.client.login(username="editor", password="password")
            self.passing_edit_tests()

