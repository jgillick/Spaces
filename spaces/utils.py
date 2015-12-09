
import re
import os


def normalize_path(path):
    """
    Normalizes a path:
     * Removes extra and trailing slashes
     * Converts special characters to underscore
    """
    path = re.sub(r'/+', '/', path)     # repeated slash
    path = re.sub(r'/*$', '', path)     # trailing slash
    
    path = [to_slug(p) for p in path.split(os.sep)]
    
    return os.sep.join(path) # preserves leading slash

def to_slug(value):
    """ 
    Convert a string to a URL slug
    """
    # Space to dashes
    value = re.sub(r'[\s_]+', '-', value) 

    # Special characters
    value = re.sub(r'[^a-z0-9\-]+', '', value, flags=re.I)

    # Extra dashes
    value = re.sub(r'\-{2,}', '-', value) 
    value = re.sub(r'(^\-)|(\-$)', '', value) 

    return value