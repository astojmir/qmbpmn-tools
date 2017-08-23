#
# ===========================================================================
#
#                            PUBLIC DOMAIN NOTICE
#               National Center for Biotechnology Information
#
#  This software/database is a "United States Government Work" under the
#  terms of the United States Copyright Act.  It was written as part of
#  the author's official duties as a United States Government employee and
#  thus cannot be copyrighted.  This software/database is freely available
#  to the public for use. The National Library of Medicine and the U.S.
#  Government have not placed any restriction on its use or reproduction.
#
#  Although all reasonable efforts have been taken to ensure the accuracy
#  and reliability of the software and data, the NLM and the U.S.
#  Government do not and cannot warrant the performance or results that
#  may be obtained by using this software or data. The NLM and the U.S.
#  Government disclaim all warranties, express or implied, including
#  warranties of performance, merchantability or fitness for any particular
#  purpose.
#
#  Please cite the author in any work or product based on this material.
#
# ===========================================================================
#
# Code author:  Aleksandar Stojmirovic
#

from . import exceptions as exc
import string, numpy

def int_validator(field, val, xmin=0, xmax=100, **kwargs):
    try:
        if val.isdigit():
            x = int(val)
            if x < xmin:
                x = xmin
            elif x > xmax:
                x = xmax
            return x
        else:
            raise exc.ValidationError(field, val)
    except ValueError, e:
        raise exc.ValidationError(field, val)

def hash_validator(field, val, **kwargs):
    try:
        int(val,16)
        return val
    except:
        raise exc.ValidationError(field, val)

def float_validator(field, val, xmin=0.0, xmax=1.0, **kwargs):
    """
    Validates floating-point form input.
    """

    try:
        y = float(val)
    except ValueError, e:
        raise exc.ValidationError(field, val)

    if y < xmin or y > xmax:
        raise exc.OutOfRangeError(field, val)

    return y

def dfcrit_validator(field, val, **kwargs):

    if val not in ['df', 'da', 'dr', 'ap']:
        raise exc.ValidationError(field, val)
    else:
        return val

def df_validator(field, val, xmin=0.0, xmax=1.0, **kwargs):
    """
    Validates damping factor from dissipation input.
    """
    return 1.0 - float_validator(field, val, xmin, xmax)

def da_validator(field, val, **kwargs):
    """
    Validates path-length input.
    """

    try:
        y = float(val)
    except ValueError, e:
        raise exc.ValidationError(field, val)
    if y < 0:
        raise exc.OutOfRangeError(field, val)
    return y


def context_group_validator(context, processed_args, **kwargs):

    sources = processed_args['source%d' % context]
    sinks = processed_args['sink%d' % context]
    dfcrit = processed_args['dfcrit%d' % context]

    if (len(sources) == 0) and (len(sinks) == 0):
        return {}
    elif (len(sources) > 0) and (len(sinks) > 0):
        context_args = {'source_nodes': sources,
                        'sink_nodes': sinks,
                        }
        if dfcrit == 'df':
            context_args['df'] = processed_args['df%d' % context]
        elif dfcrit == 'da':
            context_args['da'] = processed_args['da%d' % context]
        elif dfcrit == 'dr':
            context_args['dr'] = processed_args['dr%d' % context]

        return {'context%d' %  context: context_args}
    else:
        raise exc.PathwayError(context)

def tokenize_protein_list(s):

    separators = string.whitespace + ',;'
    table = string.maketrans(separators, ' '*len(separators))
    transformed = s.translate(table)
    protein_list = transformed.strip().split()
    return protein_list


def protein_list_validator(field, val, network, **kwargs):
    """
    Validates a list of protein identifiers.
    """

    protein_list = tokenize_protein_list(val)
    return network.validate_symbols(protein_list, field, ignore_unknown=False)

def antisink_map_validator(field, val, network, **kwargs):
    """
    Validates a list of excluded nodes.

    NOTE: ignores invalid entries rather than raising exception.
    """

    protein_list = tokenize_protein_list(val)
    valid_names = network.validate_symbols(protein_list, field,
                                           ignore_unknown=True)
    return {}.fromkeys(valid_names, 0.0)



def find_input_option(cgi_map, field_key, allowed_opts, default_opt=None):
    """
    Finds the option given by the value of cgi_map[field_key] in
    the dictionary allowed_opts.
    """

    if field_key in cgi_map:
        field_val = cgi_map[field_key]

        if field_val in allowed_opts:
            return allowed_opts[field_val], field_val
        elif default_opt:
            return default_opt
        else:
            raise exc.ValidationError(field_key, field_val)
    elif default_opt:
        return default_opt
    else:
        raise exc.InsufficientArgsError(field_key)



# THIS IS NOT USED NOW - NEEDS TO BE REDONE LATER

# from ..core.complexes import df_table_2

# def layered_context_group_validator(context, processed_args, **kwargs):

#     sources = processed_args['source%d' % context]
#     sinks = processed_args['sink%d' % context]

#     if (len(sources) == 0) and (len(sinks) == 0):
#         return {}
#     elif (len(sources) > 0) and (len(sinks) > 0):
#         return {'context%d' %  context: (sources, sinks)}
#     else:
#         raise exc.PathwayError(context)

# def df_table_validator(processed_args, **kwargs):

#     a = processed_args['df_a']
#     b = processed_args['df_b']
#     c = processed_args['df_c']

#     df_table = df_table_2(a, b, c)
#     return {'df_table': df_table}


# def layered_protein_list_validator(field, val, G, **kwargs):
#     """
#     Validates a list of identifiers for layered models.
#     """

#     valid_names = []
#     protein_list = tokenize_protein_list(val)
#     for p in protein_list:
#         try:
#             nodes = G.get_all_nodes(p)
#             valid_names.extend(map(str, nodes))
#         except KeyError:
#             raise exc.ValidationError(field, p)

#     return valid_names

# def layered_antisink_map_validator(field, val, G, **kwargs):
#     """
#     Validates antisinks for layered models.
#     """
#     valid_names = layered_protein_list_validator(field, val, G)
#     return {}.fromkeys(valid_names, 8.0)

