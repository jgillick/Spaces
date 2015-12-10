import re
from os import path

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.db import models

from .utils import normalize_path

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
            create: Creates document for path segments
                    that do not exist
        """

        from .models import Space

        if type(path) is not list:
            path = normalize_path(path).split('/')
        queryset = self.get_queryset()

        # Get space
        if space is None:
            try:
                space = Space.objects.get(path=path[0])
                path.pop(0)
            except ObjectDoesNotExist:
                raise ObjectDoesNotExist("The space '%s' does not exist" % path[0])

        # Follow the path
        doc = None
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
                        doc = self.create(title=p, path=p, parent=doc, space=space)
                    else:
                        raise ObjectDoesNotExist("Document at %s does not exist" % curPath)
        else:
            doc = space.get_root_document()

        return doc
            