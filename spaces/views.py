from django.views import generic

from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import login, mixins, get_user
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse

from .models import AccessLog, Space, Document, Revision
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

    def get_context_data(self, **kwargs):
        document = self.get_object()
        context = super(DocView, self).get_context_data(**kwargs)

        # General space list
        context["general_spaces"] = Space.objects.exclude(
            name__in=[Space.ROOT_SPACE_NAME, Space.USER_SPACE_NAME])

        # Breadcrumbs
        parent = document.parent
        context["path_documents"] = []

        if not document.is_space_root:
            context["path_documents"].insert(0, document)

        while parent is not None:
            context["path_documents"].insert(0, parent)
            parent = parent.parent

        return context

    def get(self, request, *args, **kwargs):
        document = self.get_object()

        # Add access log
        user = get_user(request)
        if user.is_anonymous():
            user = None
        AccessLog.objects.create(document=document, user=user)

        return super(DocView, self).get(request, *args, **kwargs)


class DocCreate(mixins.LoginRequiredMixin, generic.edit.UpdateView):

    """ Create a new document """

    form_class = DocumentForm
    template_name = 'spaces/document/edit.html'

    def get_object(self):
        path = self.kwargs["path"]
        doc = Document(path=path)

        return doc

    def get_form_kwargs(self):
        """ Add user to the kwargs sent to DocumentForm """
        kwargs = super(DocCreate, self).get_form_kwargs()
        kwargs["user"] = self.user
        return kwargs

    def _setup_forms(self, request, post=None):
        self.user = request.user
        self.object = self.get_object()
        rev_qs = self.object.revision_set.order_by('-created_on')

        if rev_qs.count():
            rev_qs = rev_qs.filter(pk=rev_qs[0].pk)

        form = self.get_form(self.get_form_class())
        revision_form = RevisionInlineFormset(
            post,
            instance=self.object,
            queryset=rev_qs,
            user=self.user)

        return (form, revision_form, )

    def get(self, request, *args, **kwargs):
        """ Handle GET requests. """
        form, revision_form = self._setup_forms(request)

        return self.render_to_response(
            self.get_context_data(form=form, revision_form=revision_form))

    def post(self, request, *args, **kwargs):
        """ Handle POST requests. """
        self.user = request.user
        self.object = self.get_object()

        # Parent is defined by path
        self.object.parent = None

        form = self.get_form(self.get_form_class())
        revision_form = RevisionInlineFormset(
            request.POST, instance=self.object, user=self.user)

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
            return doc
        except ObjectDoesNotExist:
            raise Http404


class DocDelete(generic.edit.DeleteView):

    """ Delete a document. """

    model = Document

    def post(self, request, *args, **kwargs):
        object = self.get_object()

        # Redirect to the parent page
        self.success_url = reverse(
            'spaces:document',
            kwargs={"path": object.parent.full_path()})

        return super(DocDelete, self).post(request, *args, **kwargs)


class LoginView(generic.edit.FormView):

    """ Login form. """

    form_class = AuthenticationForm
    template_name = 'spaces/login.html'

    def form_valid(self, form):
        self.success_url = reverse('spaces:document', kwargs={"path": ""})
        login(self.request, form.get_user())
        return super(LoginView, self).form_valid(form)