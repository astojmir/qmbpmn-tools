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

import sys
import os.path
from ...common.utils.filesys import makedirs2
from ...common.utils.filesys import check_file_exists
from .. import validators as vld
from .. import exceptions as exc
from ..response import html_response
from ..response import plain_response
from .validate import validate_program_args
from .validate import validate_output_args
from .validate import validate_term_scores_args
from .results import get_saddlesum_results
from .results import parse_saddlesum_tab_output
from .results import parse_saddlesum_tab_term_scores
from .results import save_query_data
from .results import get_saddlesum_term_scores
from .htmloutput import saddlesum_html_results
from .htmloutput import saddlesum_html_term_scores
from .svgoutput import create_and_save_image
from .etdinfo import get_etd_info


def _get_storage_path(conf):
    storage_path = os.path.join(conf.data_root, conf.enrich_storage_dir)
    makedirs2(storage_path)
    return storage_path


def process_cgi_query(cgi_map, conf):

    opts, raw_weights, termdb_file = validate_program_args(cgi_map, conf)
    out_fmt, query_id, img_format, colormap = validate_output_args(cgi_map)

    storage_path = _get_storage_path(conf)
    graphics_file = os.path.join(storage_path, '%s.svg' % query_id)
    weights_file = os.path.join(storage_path, '%s.dat' % query_id)
    command_file = os.path.join(storage_path, '%s.cmd' % query_id)

    if out_fmt == 'txt':
        output, full_args = get_saddlesum_results(opts, raw_weights,
                                                  termdb_file, 'txt',
                                                  conf.saddlesum_path)
        plain_response(output)

    elif out_fmt == 'tab':
        output, full_args = get_saddlesum_results(opts, raw_weights,
                                                  termdb_file, 'tab',
                                                  conf.saddlesum_path)
        plain_response(output)

    elif out_fmt == 'html':
        output, full_args = get_saddlesum_results(opts, raw_weights,
                                                  termdb_file, 'tab',
                                                  conf.saddlesum_path)
        section_data = parse_saddlesum_tab_output(output)
        create_and_save_image(graphics_file, img_format, conf.graphviz_path,
                              colormap, *section_data[4:])
        res = saddlesum_html_results(conf, query_id, *section_data[:4])
        html_response(res)

    save_query_data(raw_weights, full_args, weights_file, command_file)


def get_svg_image(cgi_map, conf):

    query_id = vld.hash_validator('query_id', cgi_map['query_id'])
    image_filename = '%s.svg' % query_id
    storage_path = _get_storage_path(conf)
    image_path = os.path.join(storage_path, image_filename)

    sys.stdout.write("Content-Type: image/svg+xml\n\n")
    if check_file_exists(image_path):
        with open(image_path, 'rb') as fp:
            sys.stdout.write(fp.read())


def get_term_scores(cgi_map, conf):

    term_id, command_file, out_fmt = validate_term_scores_args(cgi_map, conf)

    output = get_saddlesum_term_scores(term_id, command_file,
                                       conf.saddlesum_path, out_fmt)
    if out_fmt == 'html':
        section_data = parse_saddlesum_tab_term_scores(output)
        res = saddlesum_html_term_scores(conf, *section_data)
        html_response(res)
    else:
        plain_response(output)


def get_term_databases(cgi_map, conf):

    termdbs_path = os.path.join(conf.data_root,
                                conf.enrich_termdb_dir)
    termdbs = []
    for filename in os.listdir(termdbs_path):
        if os.path.splitext(filename)[1] == '.etd':
            etd_file = os.path.join(termdbs_path, filename)
            etd_info = get_etd_info(etd_file, conf.saddlesum_path)
            termdbs.append((etd_info['db_name'], filename))
    termdbs.sort()
    output_lines = ['\t'.join(_line) for _line in termdbs]
    output = '\n'.join(output_lines)
    return plain_response(output)


VIEWS = {'a': process_cgi_query,
         'b': get_svg_image,
         'c': get_term_scores,
         'd': get_term_databases,
         }
