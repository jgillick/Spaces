from os import path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import (
    ObjectDoesNotExist, PermissionDenied, ValidationError)
from django.core.urlresolvers import reverse
from django.db import models

from .managers import DocumentManager, SpaceManager
from .utils import normalize_path, to_slug


class Space(models.Model):

    ROOT_SPACE_NAME = '__ROOT__'
    USER_SPACE_NAME = '__USER__'

    objects = SpaceManager()

    """
    A general Space.
    """

    name = models.CharField(max_length=100, unique=True)
    path = models.CharField(max_length=40, unique=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ("view_space", "Can view a space"),
        )

    def __unicode__(self):
        return self.name

    def get_user_space_root(user):
        """
        Return the root document to a space for a specific user.
        """
        user_space = Space.objects.get(name=Space.USER_SPACE_NAME)
        doc, created = Document.objects.get_or_create(
            path=user.username,
            space=user_space,
            parent=None)

        return doc

    def get_root_document(self):
        """
        Return the root document for the space.
        """
        # Can't use get_or_create, since we don't want to find by title
        try:
            doc = Document.objects.get(
                path="",
                space=self,
                is_space_root=True,
                parent=None)
        except ObjectDoesNotExist:
            doc = Document.objects.create(
                title=self.name,
                path="",
                space=self,
                is_space_root=True,
                parent=None
            )

        return doc

    def full_clean(self, *args, **kwargs):
        self.path = to_slug(self.path)
        super(Space, self).full_clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
        super(Space, self).save(*args, **kwargs)


class Document(models.Model):

    """
    A single document.

    The actual content existing in the revisions.
    """

    objects = DocumentManager()

    path = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=100)
    is_space_root = models.BooleanField(
        "Is this a space's root document",
        default=False)
    space = models.ForeignKey('Space')
    parent = models.ForeignKey('Document', null=True, blank=True)

    class Meta:
        unique_together = ("path", "parent"),
        permissions = (
            ("view_document", "Can view a document"),
        )

    def __init__(self, *args, **kwargs):
        super(Document, self).__init__(*args, **kwargs)

        # Process space and path
        if not self.has_space() and self.parent and self.parent.has_space:
            self.space = self.parent.space
        if "path" in kwargs:
            self._process_path(kwargs["path"])

    def __unicode__(self):
        return self.title

    def latest(self):
        """ Get the latest revision """
        return self.revision_set.order_by('-id').first()

    def has_space(self):
        """
        Return the space attached to this document, otherwise, return False
        """
        try:
            return self.space
        except ObjectDoesNotExist:
            return False

    def full_path(self, inc_space=True):
        """ The full path to this document. """
        uri = self.path

        parent = self.parent
        while parent is not None:
            uri = path.join(parent.path, uri)
            parent = parent.parent

        if inc_space and self.space.name != Space.ROOT_SPACE_NAME:
            uri = path.join(self.space.path, uri)

        return uri

    def get_absolute_url(self):
        """ Get the absolute URL route to the document. """
        return reverse('spaces:document', kwargs={'path': self.full_path()})

    def _process_path(self, path):
        """ Take a path and set the space and parent """

        path = normalize_path(self.path).split("/")

        if not self.has_space():
            spacePath = path.pop(0)
            try:
                self.space = Space.objects.get(path=spacePath)
            except ObjectDoesNotExist:
                # Space might not be included in path, add it back to path
                path.insert(0, spacePath)

        parentPath = path[0:-1]
        if len(path) >= 1:
            self.path = path[-1]
        else:
            self.path = ""

        parentPath = filter(len, parentPath)  # remove empty path sections
        if parentPath:
            self.parent = Document.objects.get_by_path(
                parentPath,
                space=self.space,
                create=True)

    def view_count(self):
        """ Return the number of times this document has been viewed. """
        return self.accesslog_set.count()

    def full_clean(self, override_path_normalization=False, *args, **kwargs):
        """ Custom clean method """

        # Parent document needs to be in same space
        if (self.parent and self.has_space() and self.parent.space != self.space):
            raise ValidationError("Parent not in the same space")

        # If no space, default to parent's
        elif not self.has_space():
            if self.parent is not None:
                self.space = self.parent.space
            else:
                raise ValidationError("No space defined")

        # Convert path to parent node
        if self.path.find('/') > -1:
            self._process_path(self.path)

        # Normalize path
        elif not self.is_space_root:
            self.path = to_slug(self.path)

        # Set no parent to root document
        if self.parent is None and not self.is_space_root:
            self.parent = self.space.get_root_document()

        # If we're a root level document, we can't have the
        # same path as the space. This is to cut down on confusion
        if (not self.is_space_root and self.parent.is_space_root
                and self.path.lower() == self.space.path.lower()):
            raise ValidationError(
                "This document cannot have the same path name as it's space (%s)"
                % self.space.path)

        # User Space: Cannot create a root document that is not a username
        if self.space.name == Space.USER_SPACE_NAME and self.parent is None:
            try:
                get_user_model().objects.get(username=self.path)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist(
                    "Invalid username '%s'" % self.path)

        #  No hierarchy is allowed under the __ROOT__ space
        if self.space.name == Space.ROOT_SPACE_NAME and not self.is_space_root:
            raise ValidationError(
                "Cannot put child pages under the root space")

        super(Document, self).full_clean(*args, **kwargs)

    def save(self, override_path_normalization=False, *args, **kwargs):
        self.full_clean(override_path_normalization)

        # Save parents
        if (self.parent is not None
                and self.parent.pk is None
                and not self.is_space_root):
            self.parent.save()
            self.parent_id = self.parent.id

        super(Document, self).save(*args, **kwargs)

    def delete(self, with_children=False, *args, **kwargs):
        """
        If passed with with_children=True, all child documents will also be deleted
        """

        # Update child documents
        for d in self.document_set.all():
            if with_children:
                d.delete(with_children=True)
            else:
                d.parent = self.parent
                d.save()

        # Cannot delete root space document
        if self.is_space_root:
            raise ValidationError(
                "Cannot remove the root space document")

        super(Document, self).delete(*args, **kwargs)


class Revision(models.Model):

    """
    A revision for a document.

    Every time a document is edited, a new revision is created.
    """

    doc = models.ForeignKey('Document', verbose_name="Document")
    author = models.ForeignKey(settings.AUTH_USER_MODEL) #editable=False
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "created on %s by %s" % (self.created_on, self.author.username)

    def save(self, *args, **kwargs):
        self.full_clean()

        # If it's the same content as the current revision, don't save
        latestContent = self.doc.latest()
        if latestContent and latestContent.content == self.content:
            return

        # Otherwise, always create new revision
        else:
            self.id = None
            self.created_on = None

        super(Revision, self).save(*args, **kwargs)


class Comment(models.Model):
    """ A comment on a document """

    document = models.ForeignKey('Document')
    parent = models.ForeignKey('Comment')
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return "created on %s by %s" % (self.created_on, self.author.username)


class AccessLog(models.Model):

    """ Tracks every time a user views a document. """

    document = models.ForeignKey('Document')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True)
    accessed_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "accessed %s on %s" % (self.document.title, self.accessed_on)
