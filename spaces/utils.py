
import re


def normalize_path(path):
    """
    Normalizes a path:
     * Removes extra and trailing slashes
     * Converts special characters to underscore
    """
    path = re.sub(r'/+', '/', path)     # repeated slash
    path = re.sub(r'/*$', '', path)     # trailing slash
    path = re.sub(r'[\s_]+', '-', path) # Space to dash
    path = re.sub(r'[^a-z0-9\-\/]', '', path, flags=re.I)
    return path