
import re
import os
import uuid

from datetime import date
from django.conf import settings


def normalize_path(path):
    """
    Normalizes a path:
     * Removes extra and trailing slashes
     * Converts special characters to underscore
    """
    if path is None:
        return ""

    path = re.sub(r'/+', '/', path)     # repeated slash
    path = re.sub(r'/*$', '', path)     # trailing slash

    path = [to_slug(p) for p in path.split(os.sep)]

    return os.sep.join(path)  # preserves leading slash


def to_slug(value):
    """ Convert a string to a URL slug. """
    value = value.lower()

    # Space to dashes
    value = re.sub(r'[\s_]+', '-', value)

    # Special characters
    value = re.sub(r'[^a-z0-9\-]+', '', value, flags=re.I)

    # Extra dashes
    value = re.sub(r'\-{2,}', '-', value)
    value = re.sub(r'(^\-)|(\-$)', '', value)

    return value


def upload_file(f):
    """ Upload a file and return the URL to it. """

    # Create path under media root
    name, ext = os.path.splitext(f.name)
    name = "%s%s" % (str(uuid.uuid4()), ext)

    path = date.today().strftime("%Y")

    # Create base directory
    filepath = os.path.join(settings.MEDIA_ROOT, path)
    if not os.path.exists(filepath):
        os.makedirs(filepath)

    # Write file
    filepath = os.path.join(filepath, name)
    with open(filepath, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    # Return URL
    return os.path.join(settings.MEDIA_URL, path, name)
