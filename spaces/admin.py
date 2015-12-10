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
        if qs.count() > 0:
            return qs.order_by('-created_on').filter(id=qs[0].id)
        return qs


class DocumentAdmin(admin.ModelAdmin):
    fields = ['title', 'path', 'space']
    list_display = ['title', 'full_path']
    inlines = [RevisionInline]

class RevisionAdmin(admin.ModelAdmin):
    list_display = ('id', 'doc', 'author', 'created_on')
    list_filter = ['created_on']

admin.site.register(Document, DocumentAdmin)
admin.site.register(Space, SpaceAdmin)
admin.site.register(Revision, RevisionAdmin)