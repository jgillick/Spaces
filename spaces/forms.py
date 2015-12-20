from django import forms
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

        # Space list
        if self.instance.pk:
            # Disable selecting space if existing document
            self.fields["space"].disabled = True
        else:
            # Exclude _ROOT_ and convert _USER_ to username
            self.fields["space"].queryset = Space.objects.exclude(
                name=Space.ROOT_SPACE_NAME)
            self.fields['space'].label_from_instance = lambda obj: \
                user.username if user and obj.name == Space.USER_SPACE_NAME \
                else obj.name


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
