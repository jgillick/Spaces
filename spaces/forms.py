from django import forms
from django.forms import BaseInlineFormSet
from django.forms.models import inlineformset_factory

from .models import Document, Revision


class DocumentForm(forms.ModelForm):

    class Meta:
        fields = ['title', 'path']
        model = Document


class RevisionFormset(BaseInlineFormSet):

    def __init__(self, *args, **kwargs):
        self.author = kwargs.pop('author', None)
        super(RevisionFormset, self).__init__(*args, **kwargs)

        if self.author is not None:
            for form in self.forms:
                if form.instance.pk is None:
                    form.instance.author = self.author

    def clean(self, *args, **kwargs):
        super(RevisionFormset, self).clean(*args, **kwargs)

        # Validate the the author is the logged in user
        # for form in self.forms:
        #     print form.cleaned_data
        #     if form.cleaned_data.get('author') != self.author:
        #         form.add_error(
        #             'author',
        #             'There was an error setting the author')


RevisionInlineFormset = inlineformset_factory(
    Document,
    Revision,
    formset=RevisionFormset,
    extra=1, max_num=1,
    fields=('content',),
    # exclude=(),
    can_delete=False)
