from django.conf import settings
from django.db import models

class Space(models.Model):
    name = models.CharField(max_length=100)
    uri = models.CharField('URI', max_length=100)
    created_on = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

class Document(models.Model):
    space = models.ForeignKey('Space')
    uri = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    latest = models.ForeignKey('Revision')

    def __unicode__(self):
        return self.uri

class Revision(models.Model):
    doc = models.ForeignKey('Document')
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)

class Comment(models.Model):
    document = models.ForeignKey('Document')
    parent = models.ForeignKey('Comment')
    author = models.ForeignKey(settings.AUTH_USER_MODEL)
    content = models.TextField()
    created_on = models.DateTimeField(auto_now_add=True)
    updated_on = models.DateTimeField(auto_now=True)

class AccessLog(models.Model):
    document = models.ForeignKey('Document')
    user = models.ForeignKey(settings.AUTH_USER_MODEL)
    accessed_on = models.DateTimeField(auto_now_add=True)