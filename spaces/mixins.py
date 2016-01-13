from conf import spaces_settings

from django.contrib.auth.mixins import AccessMixin, PermissionRequiredMixin


class ViewPermissionRequiredMixin(PermissionRequiredMixin):

    """ Ensure the user has access to view a document. """

    permission_required = 'spaces.view_document'

    def dispatch(self, request, *args, **kwargs):
        if spaces_settings['AUTH_GUEST_CAN_VIEW']:
            return super(AccessMixin, self).dispatch(request, *args, **kwargs)
        return super(ViewPermissionRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class EditPermissionRequiredMixin(PermissionRequiredMixin):

    """ Ensure the user has access to edit a document. """

    permission_required = ('spaces.add_document', 'spaces.change_document')

    def dispatch(self, request, *args, **kwargs):
        if (request.user.is_authenticated() and
                spaces_settings['AUTH_ANY_USER_CAN_EDIT']):
            return super(AccessMixin, self).dispatch(request, *args, **kwargs)
        return super(EditPermissionRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class DeletePermissionRequiredMixin(EditPermissionRequiredMixin):

    """ Ensure the user has access to delete a document. """

    permission_required = 'spaces.delete_document'
