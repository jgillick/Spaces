from conf import spaces_settings


def spaces_processor(request):
    """ Set global template variables. """
    return {
        'site_name': spaces_settings['SITE_NAME']
    }
