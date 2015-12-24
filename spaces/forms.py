import re

from django import forms
from django.core.exceptions import ObjectDoesNotExist, ValidationError
from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory

from .models import Document, Revision, Space


class DocumentForm(forms.ModelForm):

    class Meta:
        fields = ['title', 'space', 'path']
        model = Document

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(DocumentForm, self).__init__(*args, **kwargs)

        # Existing document
        if self.instance.pk:
            # Disable selecting space if existing document
            self.fields["space"].disabled = True

            # Cannot change path for root document
            if self.instance.is_space_root:
                self.fields["path"].disabled = True

        # Exclude _ROOT_ and convert _USER_ to username
        self.fields["space"].queryset = Space.objects.exclude(
            name=Space.ROOT_SPACE_NAME)
        self.fields['space'].label_from_instance = lambda obj: \
            user.username if user and obj.name == Space.USER_SPACE_NAME \
            else obj.name

        # Set default path and remove double slashes
        self.initial["path"] = self.instance.full_path(inc_space=False) + "/"
        self.initial["path"] = re.sub(r'/+', '/', self.initial["path"])

    def clean_path(self):
        doc = None
        path = self.cleaned_data["path"]

        # Empty path
        if (not path
            and (not self.instance.pk or not self.instance.is_space_root)):
            raise ValidationError("A path is required")

        # Try to find another document with this pass
        else:
            try:
                doc = Document.objects.get_by_path(
                    path=path, space=self.instance.space
                )
                if not self.instance.pk or doc.pk != self.instance.pk:
                    raise ValidationError("This path already exists")
            except ObjectDoesNotExist:
                pass

        return path


class RevisionFormset(BaseInlineFormSet):

    """
    For the revision formset included with the document.
    """

    def __init__(self, *args, **kwargs):
        """ Need to instantiated with an 'author' param. """
        self.author = kwargs.pop('user', None)
        super(RevisionFormset, self).__init__(*args, **kwargs)

        # Setup values
        for form in self.forms:
            if form.instance.pk is None:
                if self.author is not None:
                    form.instance.author = self.author


RevisionInlineFormset = inlineformset_factory(
    Document,
    Revision,
    formset=RevisionFormset,
    extra=1, max_num=1,
    fields=('content',),
    can_delete=False)
