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
import os
import time
from .. import validators as vld
from .. import exceptions as exc
from ...common.utils.filesys import check_file_exists

_NUM_COLORS = 8
_COLORMAPS = ['%s%s' % (s,_NUM_COLORS) for s in \
              ['Blues', 'Reds', 'Greys', 'Greens', 'Oranges',
               'YlGn', 'YlGnBu', 'GnBu', 'RdPu', 'PuRd', 'BrBG']]
INITIAL_FORM_DATA = {'cutoff_Evalue': 1e-02,
                     'min_term_size': 2,
                     'effective_tdb_size': 0,
                     'stats': [("Lugananni-Rice (sum of weights)", 'wsum'),
                               ("One-sided Fisher's Exact test", 'hgem'),
                               ],
                     'cutoff_type': [('No cutoff','none'),
                                     ('By rank','rank'),
                                     ('By weight', 'wght')
                                     ],
                     'transform_weights': [('No transformation','none'),
                                           ('Flip signs','flip'),
                                           ('Take absolute value', 'abs')
                                           ],
                     'image_formats': [('SVG in Navigator','netmapsvg2'),
                                       ('SVG','svg')],
                     'colormaps': [(s,s.lower()) for s in _COLORMAPS],
                     }


def _fix_raw_weights(raw_weights_data):
    # Macs or windows machines may pass different line-termination characters
    lines = [s.strip() for s in raw_weights_data.split('\n')]
    return '\n'.join(lines)


def validate_program_args(cgi_map, conf):

    opts = []
    # termdb
    termdbs_path = os.path.join(conf.data_root, conf.enrich_termdb_dir)
    termdbs_map = dict((v,v) for v in os.listdir(termdbs_path) \
                       if os.path.splitext(v)[1] == '.etd')
    termdb_file = vld.find_input_option(cgi_map, 'termdb', termdbs_map)[0]
    termdb_file = os.path.join(conf.data_root, conf.enrich_termdb_dir, termdb_file)

    # weights
    raw_weights_data = cgi_map.get('raw_weights', '')
    raw_weights_data2 = cgi_map.get('raw_weights2', '')
    if len(raw_weights_data2):
        raw_weights_data = raw_weights_data2
    raw_weights = _fix_raw_weights(raw_weights_data)

    # E-value
    if 'cutoff_Evalue' in cgi_map:
        tmp = vld.float_validator('E-value', cgi_map['cutoff_Evalue'])
        opts.extend(['-e', '%.6e' % tmp])

    # Minimum term size
    if 'min_term_size' in cgi_map:
        tmp = vld.int_validator('Minimum term size', cgi_map['min_term_size'],
                                1, 10000000)
        opts.extend(['-m', '%d' % tmp])

    # Effective term database size
    if 'effective_tdb_size' in cgi_map:
        tmp = vld.float_validator('Effective database size',
                                  cgi_map['effective_tdb_size'], 0.0, 1.0e16)
        if tmp > 0.0:
            opts.extend(['-n', '%.6e' % tmp])

    # Statistics
    stats_options = ['wsum', 'hgem']
    all_stats = dict(zip(stats_options, stats_options))
    tmp = vld.find_input_option(cgi_map, 'stats', all_stats, 'wsum')[0]
    opts.extend(['-s', tmp])

    # Transform weights
    if 'transform_weights' in cgi_map:
        all_transforms = {'none': None, 'flip': 'flip', 'abs': 'abs'}
        tmp = vld.find_input_option(cgi_map, 'transform_weights',
                                    all_transforms, None)[0]
        if tmp is not None:
            opts.extend(['-t', tmp])


    # Apply cutoff
    cutoff_types = {'none': None, 'rank': 'rank', 'wght': 'wght'}
    cutoff_type = vld.find_input_option(cgi_map, 'cutoff_type', cutoff_types,
                                        None)[0]
    if cutoff_type == 'rank':
        tmp = vld.int_validator('Rank cutoff',
                                cgi_map.get('wght_cutoff', '1'),
                                1, 100000)
        opts.extend(['-r', '%d' % tmp])

    elif cutoff_type == 'wght':
        tmp = vld.float_validator('Weight cutoff',
                                  cgi_map.get('wght_cutoff', 0.0),
                                  -1e16, 1e16)
        opts.extend(['-w', '%.6e'% tmp])

    # discretize_ weights
    if 'discrete_weights' in cgi_map:
        opts.extend(['-d'])

    # ********* SECRET OPTIONS (not on the web form) ********************
    if 'use_all_weights' in cgi_map:
        opts.extend(['-a'])
    # EXCLUDED NAMESPACES - HOW ?
    return opts, raw_weights, termdb_file


def validate_output_args(cgi_map):

    query_id =  '%x' % hash(time.time())

    # Output formats
    output_formats = ['html', 'txt', 'tab']
    output_format = vld.find_input_option(cgi_map, 'output', \
                      dict(zip(output_formats, output_formats)), \
                      ('html', 'html'))[0]

    all_formats = {'svg': 'svg', 'netmapsvg2': 'netmapsvg'}
    img_format = vld.find_input_option(cgi_map, 'image_format', all_formats, 'netmapsvg')[0]

    all_colormaps = dict((c.lower(),c) for c in _COLORMAPS)
    colormap = vld.find_input_option(cgi_map, 'color_map', all_colormaps, _COLORMAPS[0])[0]

    return output_format, query_id, img_format, colormap

def validate_term_scores_args(cgi_map, conf):

    query_id = vld.hash_validator('query_id', cgi_map['query_id'])
    storage_path = os.path.join(conf.data_root, conf.enrich_storage_dir)
    weights_file = os.path.join(storage_path, '%s.dat' % query_id)
    command_file = os.path.join(storage_path, '%s.cmd' % query_id)

    # NOTE: this is safe against shell injection because we will be using
    # subprocess.popen, which does ever call shell
    # If this is deemed not OK, we can explicitly list all allowed IDs in
    # command file
    term_id = cgi_map['termid']

    # Check for missing results
    if not check_file_exists(weights_file) or \
       not check_file_exists(command_file):
        raise exc.MissingStoredResults()

    output_formats = ['html', 'txt', 'tab']
    output_format = vld.find_input_option(cgi_map, 'output', \
                      dict(zip(output_formats, output_formats)), \
                      ('html', 'html'))[0]

    return term_id, command_file, output_format
