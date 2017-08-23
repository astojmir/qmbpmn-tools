""" Miscellaneous filesystem utilities not found in the standard library."""

import sys
import os
import os.path
import errno
import shutil
from fnmatch import fnmatch
import numpy as np


def makedirs2(name, mode=0777):
    """ Creates a new directory. Does not raise exception if it exists."""

    try:
        os.makedirs(name, mode)
    except OSError, excpt:
        if excpt.errno != errno.EEXIST:
            raise


def copytree_filter(src, dst, exclude_patterns=None, symlinks=False):
    """Recursively copy a directory tree using copy2().

    Trimmed version of shutil.copytree() that allows specifying the patterns to
    exclude.
    """
    if exclude_patterns is None:
        exclude_patterns = []

    names = os.listdir(src)
    makedirs2(dst)

    errors = []
    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)
        try:
            if symlinks and os.path.islink(srcname):
                linkto = os.readlink(srcname)
                os.symlink(linkto, dstname)
            elif not any(fnmatch(srcname, ptrn) for ptrn in exclude_patterns):
                if os.path.isdir(srcname):
                    copytree_filter(srcname, dstname, exclude_patterns,
                                    symlinks)
                else:
                    shutil.copy2(srcname, dstname)
        except (IOError, os.error), why:
            errors.append((srcname, dstname, str(why)))
        # catch the Error from the recursive copytree so that we can
        # continue with other files
        except shutil.Error, err:
            errors.extend(err.args[0])
    try:
        shutil.copystat(src, dst)
    except OSError, why:
        if WindowsError is not None and isinstance(why, WindowsError):
            # Copying file access times may fail on Windows
            pass
        else:
            errors.extend((src, dst, str(why)))
    if errors:
        raise shutil.Error, errors


def check_file_exists(full_path):
    """Check if the file exists on filesystem."""

    try:
        os.stat(full_path)
        return True
    except OSError:
        pass
    return False


def import_module(module_name):
    """Dynamically import module."""

    # We insert the current working directory into sys.path
    sys.path.append(os.getcwd())

    # Helper from Python Library Reference
    mod = __import__(module_name)
    components = module_name.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod


def write_string_list(fp, str_lst, write_list_length=True):
    """Write list of strings into binary file."""
    if write_list_length:
        fp.write(np.array([len(str_lst)], dtype='<u4'))
    buf = "%s\0" % '\0'.join(str_lst)
    fp.write(np.array([len(buf)], dtype='<u4'))
    fp.write(buf)

def read_string_list(fp, read_list_length=True):
    """Read list of strings from binary file."""
    if read_list_length:
        fp.read(4) # This is discarded
    blen = int(np.frombuffer(fp.read(4), '<u4')[0])
    buf = fp.read(blen)
    return buf.split('\0')[:-1]
