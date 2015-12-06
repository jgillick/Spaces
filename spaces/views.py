from django.views import generic

from .models import Space, Document


class DocView(generic.DetailView):
    model = Document
    template_name = 'spaces/index.html'


class UserDocView(generic.DetailView):
    model = Document
    template_name = 'spaces/index.html'


class IndexView(generic.ListView):
    template_name = 'spaces/index.html'

    def get_queryset(self):
        """Return the last five published questions."""
        return Space.objects