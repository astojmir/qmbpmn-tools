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


import os.path
from ...common.utils.pickling import check_object
from ...common.utils.pickling import restore_object
from .. import validators as vld
from .. import exceptions as exc
from ..SaddleSum.runs import process_cgi_query
from ...ITMProbe import commands

_NUM_COLORS = 8
_COLORMAPS = ['%s%s' % (s,_NUM_COLORS) for s in \
              ['Blues', 'Reds', 'Greys', 'Greens', 'Oranges',
               'YlGn', 'YlGnBu', 'GnBu', 'RdPu', 'PuRd', 'BrBG']]
INITIAL_FORM_DATA = {'cutoff_Evalue': 1e-02,
                     'stats': [("Lugananni-Rice (sum of weights)", 'wsum'),
                               ("One-sided Fisher's Exact test", 'hgem'),
                               ],
                     "min_term_size": 2,
                     'cutoff_type': [('No cutoff','none'),
                                     ('By rank','rank'),
                                     ('By weight', 'wght')
                                     ],
                     'image_formats': [('SVG in Navigator','netmapsvg2'),
                                       ('SVG','svg')],
                     'colormaps': [(s,s.lower()) for s in _COLORMAPS],
                     }
FORM_FIELDS = ['cutoff_Evalue',
               "min_term_size",
               'stats',
               'transform_weights',
               'cutoff_type',
               'wght_cutoff',
               'discrete_weights',
               'output',
               'image_format',
               'color_map',
               ]

def form_input_options(www_model, query_id, conf):

    allowed_weights = [rndr for rndr in www_model.display_options.renderings \
                       if rndr.form_value != 'mix']
    opts = {'query_id': query_id,
            'weights': [(rndr.text, rndr.form_value) \
                        for rndr in allowed_weights],
            'termdb_names': www_model.enrich_termdb_names,
            }
    opts.update(INITIAL_FORM_DATA)
    return opts


def enrich_query(cgi_map, conf):

    storage_path = os.path.join(conf.data_root, conf.ITMProbe_storage_dir)
    cgi_args = {'exclude_warning_types': '0|1'}
    query_id = vld.hash_validator('query_id', cgi_map['query_id'])

    if check_object(storage_path, '%s' % query_id):
        www_model = restore_object(storage_path, query_id)
    else:
        raise exc.MissingStoredResults()

    termdb = int(cgi_map['termdb'])
    termdb_file = os.path.split(www_model.enrich_files[termdb])[1]
    cgi_args['termdb'] = termdb_file

    # Weights
    allowed = dict((r.form_value, r) \
                   for r in www_model.display_options.renderings
                   if r.form_value != 'mix')
    rndr, _ = vld.find_input_option(cgi_map, 'weights', allowed)

    weights = commands.get_saddlesum_weights([www_model.itm_path],
                                             rndr.value_attr)
    raw_weights = ['%s\t%.8e\n' % w for w in weights]
    cgi_args['raw_weights'] = ''.join(raw_weights)

    # Extract other params from cgi_map
    for k in FORM_FIELDS:
        if k in cgi_map:
            cgi_args[k] = cgi_map[k]

    conf.error_template = 'enrich/error.html'
    return process_cgi_query(cgi_args, conf)
