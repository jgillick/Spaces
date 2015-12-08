from os import path

from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.db import models

from .managers import DocumentManager
from .document import normalize_path


class Space(models.Model):
    """ A general Space """

    name = models.CharField(max_length=100)
    path = models.CharField(max_length=40)
    created_on = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     permissions = (
    #         ("view_documents", "Can view documents in this space"),
    #         ("add_document", "Can add documents in this space"),
    #         ("edit_document", "Can edit documents in this space"),
    #         ("delete_document", "Can remove documents in this space"),
    #     )

    def __unicode__(self):
        return self.name


class Document(models.Model):
    """ A single document.
        The actual content existing in the revisions. """

    objects = DocumentManager()

    path = models.CharField('URL Slug', max_length=100)
    title = models.CharField(max_length=100)
    parent = models.ForeignKey('Document', null=True, blank=True)
    space = models.ForeignKey('Space')

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

    def full_uri(self):
        """ 
        Return the full URI path to this document from the space forward 
        """

        uri = self.path
        parent = self.parent
        while parent is not None:
            uri = path.join(parent.path, uri)
            parent = parent.parent
        uri = path.join(self.space.path, uri)

        return uri

    def full_clean(self, *args, **kwargs):
        """ Custom clean method """

        # Parent document needs to be in same space
        if (self.parent and self.has_space() and self.parent.space != self.space):
            raise ValidationError("Parent not in the same space")

        # If no space, default to root or take parent's
        elif not self.has_space():
            if self.parent is not None:
                self.space = self.parent.space
            else:
                raise ValidationError("No space defined")

        # Convert path to parent node
        if self.path.find('/') > -1:
            path = normalize_path(self.path).split("/")
            parentPath = path[0:-1];

            self.path = path[-1]
            self.parent = Document.objects.get_by_path(
                parentPath, 
                space=self.space, 
                create=True)

        # If we're a root level document, we can't have the 
        # same path as the space. This is to cut down on confusion
        if (self.parent is None 
            and self.path.lower() == self.space.path.lower()):
            raise ValidationError(
                "This document cannot have the same path name as it's space (%s)" 
                % self.space.path )

        super(Document, self).clean(*args, **kwargs)

    def save(self, *args, **kwargs):
        self.full_clean()
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

        super(Document, self).delete(*args, **kwargs)


class Revision(models.Model):
    """ A revision for a document.
        Every time a document is edited, a new revision is created """

    doc = models.ForeignKey('Document', verbose_name="Document")
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "created on %s by %s" % (self.created_on, self.author.username)

    def save(self, *args, **kwargs):
        self.full_clean()

        # Every time we save a revision, it should create a new revision
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
    """ An access log is generated every time a user views a document """

    document = models.ForeignKey('Document')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    accessed_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "accessed %s on %s" % (self.document.title, self.accessed_on)

