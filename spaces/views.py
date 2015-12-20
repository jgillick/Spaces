from django.views import generic

from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import login, mixins
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist

from .models import Space, Document, Revision
from .forms import DocumentForm, RevisionInlineFormset


class DocView(generic.DetailView):

    """ View a document. """

    model = Document
    template_name = 'spaces/document/view.html'

    def get_object(self):
        try:
            document = Document.objects.get_by_path(self.kwargs["path"])
        except ObjectDoesNotExist:
            document = None
        return document


class DocCreate(mixins.LoginRequiredMixin, generic.edit.UpdateView):

    """ Create a new document """

    form_class = DocumentForm
    template_name = 'spaces/document/edit.html'

    def get_object(self):
        doc = Document(path=self.kwargs["path"])

        try:
            doc.parent = Document.objects.get_by_path(self.kwargs["path"])
        except ObjectDoesNotExist:
            pass

        doc.path = doc.full_path(inc_space=False)
        return doc

    def get(self, request, *args, **kwargs):
        """ Handles GET requests. """
        self.object = self.get_object()
        rev_qs = self.object.revision_set.order_by('-created_on')

        if rev_qs.count():
            rev_qs = rev_qs.filter(pk=rev_qs[0].pk)

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        revision_form = RevisionInlineFormset(
            instance=self.object,
            queryset=rev_qs)
        return self.render_to_response(
            self.get_context_data(form=form,
                                  revision_form=revision_form))

    def post(self, request, *args, **kwargs):
        """ Handles POST requests. """
        self.object = self.get_object()

        form_class = self.get_form_class()
        form = self.get_form(form_class)
        revision_form = RevisionInlineFormset(
            request.POST, instance=self.object, author=request.user)

        if (form.is_valid() and revision_form.is_valid()):
            return self.form_valid(form, revision_form)
        return self.form_invalid(form, revision_form)

    def form_valid(self, form, revision_form):
        """ All good. Finish up and save. """
        self.object = form.save()

        revision_form.instance = self.object
        revision_form.save()

        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self, form, revision_form):
        """
        Called if a form is invalid. Re-renders the context data with the
        data-filled forms and errors.
        """
        return self.render_to_response(
            self.get_context_data(form=form,
                                  revision_form=revision_form))


class DocUpdate(DocCreate):

    """ Edit a document. """

    def get_object(self):
        try:
            doc = Document.objects.get_by_path(self.kwargs["path"])
            doc.path = doc.full_path(inc_space=False)
            return doc
        except ObjectDoesNotExist:
            raise Http404


class LoginView(generic.edit.FormView):

    """ Login form. """

    form_class = AuthenticationForm
    template_name = 'spaces/login.html'
    success_url = '/'

    def form_valid(self, form):
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)