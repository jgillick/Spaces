from django import forms
from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory

from .models import Document, Revision


class DocumentForm(forms.ModelForm):

    class Meta:
        fields = ['title', 'space', 'path']
        model = Document


class RevisionFormset(BaseInlineFormSet):

    """
    For the revision formset included with the document.
    """

    def __init__(self, *args, **kwargs):
        """ Need to instantiated with an 'author' param. """
        self.author = kwargs.pop('author', None)
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
