from django.contrib.auth import get_user_model 
from django.core.exceptions import ValidationError
from django.test import TestCase

from spaces.models import Space, Document, Revision


class SpaceTestCase(TestCase):
    """ Test Space Models """

    def setUp(self):
        pass

    def test_root_space_should_be_present(self):
        """ The default application should at least have a __ROOT__ space """
        space = Space.objects.first()
        self.assertEqual(space.name, '__ROOT__')


class DocumentTestCase(TestCase):

    def setUp(self):
        self.space = Space.objects.create(name='My Space!', path='mine')

        # Document hierarchy 
        self.doc_foo = Document.objects.create(
            title='Foo', path='foo', space=self.space)
        self.doc_bar = Document.objects.create(
            title='Bar', path='bar', parent=self.doc_foo)
        self.doc_baz = Document.objects.create(
            title='Baz', path='baz', parent=self.doc_bar)

        # Create hierarchy by URI path
        self.doc_uri = Document.objects.create(
            title='Quick Fox', path='quick/brown/fox', space=self.space)

        # Root document
        root = Space.objects.get(name='__ROOT__')
        self.doc_root = Document.objects.create(
            title='Root doc', path='hello', space=root)

    def test_create_document_without_space(self):
        """ All documents belong in a space """
        with self.assertRaises(Exception):
            Document.objects.create(title='Orphan', path='annie')

    def test_path_query_finder(self):
        """ Find by full URI path """
        doc = Document.objects.get_by_path('mine/foo/bar/baz')
        self.assertEqual(doc, self.doc_baz)

    def test_path_with_extra_slashes(self):
        """ 
        Tests that paths are normalized of extra slashed before searching 
        """
        doc = Document.objects.get_by_path('mine/foo/bar///baz/')
        self.assertEqual(doc, self.doc_baz)

    def test_leading_slash_matches_root(self):
        """
        If a path has a leading slash, it matches the root space
        """
        doc = Document.objects.get_by_path('/hello')
        self.assertEqual(doc, self.doc_root)

    def test_cannot_have_parent_in_another_space(self):
        """ A document cannot have a parent that belongs to another space """
        with self.assertRaises(ValidationError):
            Document.objects.create(
                title='Wrong  parent', 
                path='wrong', 
                parent=self.doc_root, 
                space=self.space)

    def test_space_in_inferred_from_parent(self):
        """ If creating a document without a space, it's assumed from the parent """
        self.assertEqual(self.doc_bar.space.path, self.space.path)

    def test_create_with_full_uri(self):
        """ Create a document with full URI path """
        uri = 'foo/bar/baz/boo/foo'
        doc = Document.objects.create(title='Foo', path=uri, space=self.space)

        self.assertEqual(doc.path, 'foo')
        self.assertEqual(doc.full_uri(), "%s/%s" % (self.space.path, uri))


class RevisionTestCase(TestCase):
    """ Test Document Revision Models """

    def setUp(self):
        space = Space.objects.get(path='')
        user = get_user_model().objects.create_user(
            username='bob', 
            email='bob@dobbs.com', 
            password='noneofyourbusiness')

        # Document with 2 revisions
        self.doc = Document.objects.create(title='Foo', path='foo', space=space)
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

