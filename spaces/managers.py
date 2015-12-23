import re
from os import path

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .utils import normalize_path


class SpaceManager(models.Manager):

    """ Custom space queryset object """

    def get_by_path(self, path):
        """
        Return the space for a path string.
        """
        from .models import Space

        if type(path) is not list:
            path = normalize_path(path).split('/')

        rootPath = path.pop(0)
        if rootPath:
            try:
                return Space.objects.get(path=rootPath)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist(
                    "Space at %s does not exist" % rootPath)
        else:
            Space.objects.get(name=Space.ROOT_SPACE_NAME)


class DocumentManager(models.Manager):

    """ Custom document queryset object """

    def get_by_path(self, path, space=None, create=False):
        """
        Get a document from a full URI path, including space.

        Args:
            path: Full path to the document:
                  <space>/<path>/<path>/<path>
            space: The space the path is under. If not set, the
                   first path segment is assumed to be the space
            create: Creates document objects for path segments
                    that do not exist. (these will not be saved)
        """

        from .models import Document, Space

        queryset = self.get_queryset()

        if type(path) is not list:
            path = normalize_path(path).split('/')

        # Get space
        if space is None:
            rootPath = path.pop(0)
            try:
                space = Space.objects.get(path=rootPath)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist(
                    "Document at '%s' does not exist" % rootPath)

        # Follow the path
        doc = space.get_root_document()
        curPath = space.path
        if len(path):
            for p in path:
                curPath += "/%s" % p
                try:
                    doc = queryset.get(
                        path=p,
                        parent=doc,
                        space=space)
                except ObjectDoesNotExist:
                    if create:
                        doc = Document(
                            title=p, path=p, parent=doc, space=space)
                    else:
                        raise ObjectDoesNotExist(
                            "Document at %s does not exist" % curPath)

        return doc


class RevisionQuerySet(models.Manager):
    def all(self):
        return self.get_queryset().order_by('-created_on')
