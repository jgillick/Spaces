from django.contrib.auth import get_user_model 
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.test import TestCase

from spaces.models import Space, Document, Revision, \
                          ROOT_SPACE_NAME, USER_SPACE_NAME, ROOT_DOC_NAME


class SpaceTestCase(TestCase):
    """ Test Space Models """

    def test_root_space_should_be_present(self):
        """ The default application should have a __ROOT__ space """
        Space.objects.get(name=ROOT_SPACE_NAME)

    def test_user_space_should_be_present(self):
        """ The default application should have a __USER__ space """
        Space.objects.get(name=USER_SPACE_NAME)

    def test_convert_path_to_slug(self):
        """ Convert special characters in path """
        space = Space.objects.create(
            name='Test Space', path=' this-is / a !$ test  ')
        self.assertEqual(space.path, 'this-is-a-test')



class DocumentTestCase(TestCase):
    """ 
    Test the Document Model 
    """

    def setUp(self):
        self.space = Space.objects.create(name='My Space!', path='mine')

        self.user = get_user_model().objects.create_user(
            username='bob', 
            email='bob@dobbs.com', 
            password='noneofyourbusiness')

        # Document hierarchy 
        self.doc_foo = Document.objects.create(
            title='Foo', 
            path='foo', 
            space=self.space)
        self.doc_bar = Document.objects.create(
            title='Bar', 
            path='bar', 
            parent=self.doc_foo)
        self.doc_baz = Document.objects.create(
            title='Baz', 
            path='baz', 
            parent=self.doc_bar)

        # Create hierarchy by full path
        self.doc_uri = Document.objects.create(
            title='Quick Fox', 
            path='quick/brown/fox', 
            space=self.space)

        # Root document
        root = Space.objects.get(name=ROOT_SPACE_NAME)
        self.doc_root = Document.objects.create(
            title='Root doc', 
            path='hello', 
            space=root)

    def test_create_document_without_a_space(self):
        """ All documents belong in a space """
        with self.assertRaises(ValidationError):
            Document.objects.create(
                title='Orphan', path='annie')

    def test_root_space_doc_path(self):
        """
        Get the space root document by path
        """
        doc = Document.objects.get_by_path('mine')
        self.assertEqual(doc.space.path, self.space.path)
        self.assertEqual(doc.path, ROOT_DOC_NAME)
        self.assertEqual(doc.parent, None)

    def test_path_query_finder(self):
        """ Find document by full path """
        doc = Document.objects.get_by_path('mine/foo/bar/baz')
        self.assertEqual(doc, self.doc_baz)

    def test_path_with_extra_slashes(self):
        """ 
        Extra slashes in a path should be ignored when searching
        """
        doc = Document.objects.get_by_path('mine/foo/bar///baz/')
        self.assertEqual(doc, self.doc_baz)

    def test_leading_slash_matches_root(self):
        """
        If a path has a leading slash, it matches the root space
        """
        doc = Document.objects.get_by_path('/hello')
        self.assertEqual(doc, self.doc_root)

    def test_space_in_inferred_from_parent(self):
        """ 
        If creating a document without a space, it's assumed from the parent
        """
        self.assertEqual(self.doc_bar.space.path, self.space.path)

    def test_cannot_have_parent_in_another_space(self):
        """ 
        A document cannot have a parent that belongs to another space 
        """
        with self.assertRaises(ValidationError):
            Document.objects.create(
                title='Wrong  parent', 
                path='wrong', 
                parent=self.doc_root, 
                space=self.space)

    def test_create_with_full_path(self):
        """ 
        Create a document with full path 
        """
        uri = 'foo/bar/baz/boo/foo'
        doc = Document.objects.create(
            title='Foo', path=uri, space=self.space)

        self.assertEqual(doc.path, 'foo')
        self.assertEqual(doc.full_path(), "%s/%s" % (self.space.path, uri))

    def test_first_doc_cannot_match_space(self):
        """ 
        No document immediate under the space, can share the space name 
        """
        with self.assertRaises(ValidationError):
            doc = Document.objects.create(
                title='Wrong', 
                path=self.space.path, 
                space=self.space)

    def test_delete_document_in_path(self):
        """
        When deleting a document in the middle of the path, all children should be assigned 
        to the parent above
        """
        self.doc_bar.delete()
        baz = Document.objects.get(path="baz")
        self.assertEqual(baz.parent.path, self.doc_foo.path)

    def test_delete_all_in_path(self):
        """
        Delete a document and all it's children with the `with_children` flag
        """
        self.doc_bar.delete(with_children=True)
        with self.assertRaises(ObjectDoesNotExist):
            Document.objects.get_by_path('mine/foo/bar/baz')

    def test_special_characters_in_path(self):
        """
        Path elements should have special characters parsed out
        """
        path = "it's alive. bang!!bang! hash#hash"
        expected = "its-alive-bangbang-hashhash"
        doc = Document.objects.create(
            title='Test Path', 
            path=path, 
            space=self.space)

        self.assertEqual(doc.path, expected)

    def test_convert_path_to_slug(self):
        """ Convert special characters in path """
        space = Space.objects.create(name='Test Space', path=' this-is / a !$ test  ')
        self.assertEqual(space.path, 'this-is-a-test')


class UserSpaceTestCase(TestCase):
    """
    A User Space, is a special space reserved for a user
    """

    def setUp(self):
        self.space = Space.objects.get(name=USER_SPACE_NAME)

    def test_space_path(self):
        """
        Ensure that documents cannot be put in the root path.
        That part of the path is reserved for the username:
        /user/<username>/
        """
        with self.assertRaises(ValidationError):
            doc = Document.objects.create(
                title='Bad', 
                path='user/not_a_user', 
                space=self.space)


class RevisionTestCase(TestCase):
    """ 
    Test Document Revision Models 
    """

    def setUp(self):
        space = Space.objects.get(path='')
        user = get_user_model().objects.create_user(
            username='bob', 
            email='bob@dobbs.com', 
            password='noneofyourbusiness')

        # Document with 2 revisions
        self.doc = Document.objects.create(
            title='Foo', path='foo', space=space)
        rev = Revision.objects.create(
            content='Lorem ipsum dolor sit amet', 
            author=user, 
            doc=self.doc)

        rev.content = 'Sed dignissim lacinia nunc.'
        rev.save()

    def test_multiple_revisions(self):
        """ If a revision is saved, another revision will be created """
        self.assertEqual(self.doc.revision_set.count(), 2)

    def test_correct_revision(self):
        """ A document should always reference the latest revision """
        self.assertEqual(self.doc.latest().content, 'Sed dignissim lacinia nunc.')

    def test_delete_revisions(self):
        """
        Deleting a document should remove all revisions
        """
        self.doc.delete()
        self.assertEqual(Revision.objects.count(), 0)
