"""
Routines for storing and retrieving data objects from JSON files.
"""

try:
    import json
except ImportError:
    import simplejson as json


# ************************************************************************
# Monkey patching json string decoder to return strings instead of unicode
import json.decoder

if json.decoder.c_scanstring is not None:
    def _new_scanstring(*args, **kwargs):
        data, end = json.decoder.c_scanstring(*args, **kwargs)
        return str(data), end
else:
    def _new_scanstring(*args, **kwargs):
        data, end = json.decoder.py_scanstring(*args, **kwargs)
        return str(data), end

json.decoder.scanstring = _new_scanstring
# ************************************************************************

def _long_list_of_short_strings(lst):

    if all(isinstance(s, str) for s in lst) and \
       sum(len(s) for s in lst) / float(len(lst)) < 8.0:
        return True
    return False
    


class _JSONEncoder2(json.JSONEncoder):

    def _iterencode_list(self, lst, markers=None):
        # Copied from cannonical implementation and slightly modified

        if not lst:
            yield '[]'
            return
        if markers is not None:
            markerid = id(lst)
            if markerid in markers:
                raise ValueError("Circular reference detected")
            markers[markerid] = lst
        yield '['

        special_case = _long_list_of_short_strings(lst)

        if self.indent is not None and len(lst) > 3 and not special_case: # changed here 
            self.current_indent_level += 1
            newline_indent = self._newline_indent()
            separator = self.item_separator + newline_indent
            yield newline_indent
        else:
            newline_indent = None
            separator = self.item_separator

        for i, value in enumerate(lst):
            if i == 0:
                pass
            else:
                yield separator
                if special_case and (i+1) % 10 == 0:
                    yield self._newline_indent() 
            for chunk in self._iterencode(value, markers):
                yield chunk

        if newline_indent is not None:
            self.current_indent_level -= 1
            yield self._newline_indent()
        yield ']'
        if markers is not None:
            del markers[markerid]


def save_data_object(obj, obj_file):
    """Store object in a readable JSON file."""

    encoder = _JSONEncoder2(indent=2)

    if hasattr(obj_file, 'write'):
        obj_file.write(encoder.encode(obj))
    else:
        with open(obj_file, 'wb') as fp:
            fp.write(encoder.encode(obj))


def restore_data_object(obj_file):
    """Retrieve object from JSON file.

    Converts JSON unicode strings to Python2 strings.
    """

    decoder = json.JSONDecoder(encoding='ascii')
    if hasattr(obj_file, 'read'):
        obj = decoder.decode(obj_file.read())
    else:
        with open(obj_file, 'rb') as fp:
            obj = decoder.decode(fp.read())
    return obj
