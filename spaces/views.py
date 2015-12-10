from django.views import generic

from django.contrib.auth import login
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist

from .models import Space, Document


class DocView(generic.DetailView):
    model = Document
    template_name = 'spaces/document.html'

    def get_object(self):
        try:
            document = Document.objects.get_by_path(self.kwargs["slug"])
        except ObjectDoesNotExist:
            document = None
        return document


class UserDocView(generic.DetailView):
    model = Document
    template_name = 'spaces/index.html'


class IndexView(generic.ListView):
    template_name = 'spaces/index.html'

    def get_queryset(self):
        """Return the last five published questions."""
        return Space.objects

class LoginView(generic.edit.FormView):
    form_class = AuthenticationForm
    template_name = 'spaces/login.html'
    success_url = '/'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)