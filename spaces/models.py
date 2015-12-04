from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

class Space(models.Model):
    """ A general Space """

    name = models.CharField(max_length=100)
    uri = models.CharField('URI', max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        permissions = (
            ("view_documents", "Can view documents in this space"),
            ("add_document", "Can add documents in this space"),
            ("edit_document", "Can edit documents in this space"),
            ("delete_document", "Can remove documents in this space"),
        )

    def __unicode__(self):
        return self.name

class UserSpace(models.Model):
    """ Every user has their own space that only they 
        can create/edit content in """

    user = models.ForeignKey(settings.AUTH_USER_MODEL)

class Document(models.Model):
    """ A single document. 
        The actual content existing in the revisions. """

    uri = models.CharField('URL Slug', max_length=100)
    title = models.CharField(max_length=100)

    # Belongs to either a Space or a UserSpace
    space_models = models.Q(app_label="spaces", model='Space') \
        | models.Q(app_label="spaces", model='UserSpace')
    space_type = models.ForeignKey(ContentType, 
        on_delete=models.CASCADE,
        limit_choices_to=space_models)
    space_id = models.PositiveIntegerField()
    space = GenericForeignKey('space_type', 'space_id')

    class Meta:
        permissions = (
            ("view_document", "Can view a document")
        )

    def __unicode__(self):
        return self.title

class Revision(models.Model):
    """ A revision for a document.
        Every time a document is edited, a new revision is created """

    doc = models.ForeignKey('Document', verbose_name="Document")
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return "created on %s by %s" % (self.created_on, self.author.username)

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

