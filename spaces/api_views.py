from rest_framework import generics

from .models import AccessLog, Document, Revision, Space
from .serializers import DocumentSerializer, SpaceSerializer


class SpaceList(generics.ListCreateAPIView):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer


class SpaceDetail(generics.RetrieveAPIView):
    queryset = Space.objects.all()
    serializer_class = SpaceSerializer

    def get_object(self):
        try:
            doc = Space.objects.get_by_path(self.kwargs["path"])
            return doc
        except ObjectDoesNotExist:
            raise Http404


class DocumentDetail(generics.RetrieveAPIView):
    queryset = Document.objects.all()
    serializer_class = DocumentSerializer

    def get_object(self):
        try:
            doc = Document.objects.get_by_path(self.kwargs["path"])
            return doc
        except ObjectDoesNotExist:
            raise Http404
