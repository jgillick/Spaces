from django import forms
from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory

from .models import Document, Revision


class DocumentForm(forms.ModelForm):

    class Meta:
        fields = ['title', 'path']
        model = Document


class RevisionFormset(BaseInlineFormSet):
    def set_author(self, author):
        self.cleaned_data[0]['author'] = author
        print self.cleaned_data

    def clean(self):
        super(RevisionFormset, self).clean()

RevisionInlineFormset = inlineformset_factory(
    Document,
    Revision,
    formset=RevisionFormset,
    extra=1, max_num=1,
    fields=('content',),
    can_delete=False)
