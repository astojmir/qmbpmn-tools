""" Store retrieves pickles from files."""

import os
import cPickle
import os.path

def save_object(obj, storage_path, file_rootname, ext='.pkl'):
    """
    Stores object as a pickle.
    """
    filename = os.path.join(storage_path, '%s%s' % (file_rootname, ext))
    with open(filename, 'wb') as fp:
        cPickle.dump(obj, fp, -1)

def restore_object(storage_path, file_rootname, ext='.pkl'):
    """
    Retrieves object from a pickle.
    """
    filename = os.path.join(storage_path, '%s%s' % (file_rootname, ext))
    with open(filename, 'rb') as fp:
        obj = cPickle.load(fp)
    return obj

def check_object(storage_path, file_rootname, ext='.pkl'):
    """
    Checks if pickled object exists.
    """
    filename = os.path.join(storage_path, '%s%s' % (file_rootname, ext))
    try:
        os.stat(filename)
        return True
    except OSError, _:
        return False
