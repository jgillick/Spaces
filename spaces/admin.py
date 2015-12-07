from django.contrib import admin

from .models import Document, Revision, Space

class SpaceAdmin(admin.ModelAdmin):
    list_display = ('name', 'path')


class RevisionInline(admin.StackedInline):
    model = Revision
    ordering = ['-created_on']
    max_num = 1

    def get_queryset(self, request):
        """ Only return the latest revision """
        qs = super(RevisionInline, self).get_queryset(request)
        return qs.order_by('-created_on').filter(id=qs[0].id)


class DocumentAdmin(admin.ModelAdmin):
    fields = ['title', 'path']
    inlines = [RevisionInline]

    def save_model(self, request, obj, form, change):
        """ Add __ROOT__ as the default space """
        space = Space.objects.filter(id=1)[0]
        obj.space = space
        obj.save()

    def save_formset(self, request, form, formset, change):
        """ Create a new revision on save """

        revisions = formset.save(commit=False)
        rev = revisions[0]
        newRev = Revision(doc=rev.doc, author=rev.author, content=rev.content)
        newRev.save()

        formset.save_m2m()

class RevisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'doc', 'author', 'created_on')
    list_filter = ['created_on']

admin.site.register(Document, DocumentAdmin)
admin.site.register(Space, SpaceAdmin)
admin.site.register(Revision, RevisionAdmin)