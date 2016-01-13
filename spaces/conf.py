from django.conf import settings

# Default settings
spaces_settings = {
    # The name that is shown at the top of the page
    'SITE_NAME': "Spaces",

    ###############################
    # AUTH SETTINGS
    ###############################

    # Can unauthenticated user view documents
    'AUTH_GUEST_CAN_VIEW': True,

    # Any authenticated user can view/create/edit documents
    # If set to False, users have to have the correct permissions to do
    # anything in spaces. In that case, users can also be assigned to the
    # following helpful groups:
    #  * 'Spaces Viewer' - Can only view documents
    #  * 'Spaces Editor' - Can view, create, edit and remove documents
    'AUTH_ANY_USER_CAN_EDIT': True
}

# Reserved root slug names
RESERVED_ROOT_URLS = [
    'account',
    'user',
    's',
    '_add_',
    '_edit_',
    '_delete_',
    '_info_',
    '_revision_'
]


def merge_settings():
    """ Merge global settings with space_settings. """
    for k, v in spaces_settings.iteritems():
        global_key = "SPACES_%s" % k
        spaces_settings[k] = getattr(settings, global_key, v)

merge_settings()
