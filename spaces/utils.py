
import re


def normalize_path(path):
    """
    Takes a path and removes extra or trailing slashes
    """
    path = re.sub(r'/*$', '', path)
    path = re.sub(r'/+', '/', path)
    return path