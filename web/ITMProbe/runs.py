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
import os
import gzip
from cStringIO import StringIO
import numpy as np
from .. import exceptions as exc
from .. import validators as vld
from ..response import html_response
from ...common.utils.filesys import makedirs2
from ...common.utils.pickling import check_object, restore_object
from ...common.utils.jinjaenv import get_jinja_env
from ...common.graphics import image_processors as imp

from .cvterm_analysis import form_input_options
from .cvterm_analysis import enrich_query
from ...ITMProbe import commands


OUTPUT_FORMATS = ['html', 'txt', 'csv']

def _get_networks(conf):

    # Right now independent on model class
    # but that can change in future

    network_path = os.path.join(conf.data_root,
                                conf.ITMProbe_network_dir)
    network_files = []
    for filename in os.listdir(network_path):
        if filename[-7:] == 'net.cfg':
            network_files.append(filename)
    network_files.sort()
    networks = dict(('inet%2.2d' % i, os.path.join(network_path, nf)) \
      for i,nf in enumerate(network_files))

    return networks


def _get_layout_id(layout_args):
    """
    Get a hash value to represent a unique layout id per run.
    """
    # Extremely simple, fast; uses builtin hash
    keys = sorted(layout_args.keys())
    i = hash(tuple([layout_args[key] for key in keys]))
    hash_val = long(np.uint32(i))
    return '%X' % hash_val


def _get_storage_path(conf):
    storage_path = os.path.join(conf.data_root, conf.ITMProbe_storage_dir)
    makedirs2(storage_path)
    return storage_path


def run_www_model(cgi_map, conf):

    www_model_class, _ = vld.find_input_option(cgi_map, 'model_type',\
      dict( (M.html_value, M) for M in conf.ITMProbe_imported_models ))

    storage_path = _get_storage_path(conf)
    networks = _get_networks(conf)

    mdata = www_model_class()

    rendering_url = mdata.run_model(cgi_map, networks, storage_path,
                                    conf.saddlesum_path)
    _, output_tag = vld.find_input_option(cgi_map, 'output', \
                      dict(zip(OUTPUT_FORMATS, OUTPUT_FORMATS)), \
                      ('html', 'html'))
    rendering_url += '&output=%s' % output_tag

    jinja_env = get_jinja_env(conf)
    tmpl = jinja_env.get_template('ITMProbe/results1.html')

    res = tmpl.render(rendering_url=rendering_url,
                      query_id = mdata.query_id,
                      warning_msgs=mdata.warning_msgs)
    html_response(res)


def layout_www_model(cgi_map, conf):

    storage_path = _get_storage_path(conf)
    query_id = vld.hash_validator('query_id', cgi_map['query_id'])
    if check_object(storage_path, '%s' % query_id):
        mdata = restore_object(storage_path, query_id)
    else:
        raise exc.MissingStoredResults()

    output_format, _ = vld.find_input_option(cgi_map, 'output', \
                      dict(zip(OUTPUT_FORMATS, OUTPUT_FORMATS)), \
                      ('html', 'html'))

    if output_format == 'txt':

        layout_args = mdata.display_options.validate_display_args(cgi_map)
        sys.stdout.write("Content-Type: text/plain\n\n")
        commands.report(mdata.itm_path, 'txt',
                        max_rows= layout_args['max_rows'],
                        order_by= layout_args['order_by'],
                        use_participation_ratio=layout_args['use_participation_ratio'],
                        cutoff_value=layout_args['cutoff_value']
                        )

    elif output_format == 'csv':

        sys.stdout.write("Content-Type: text/csv\n")
        sys.stdout.write("Content-Disposition: attachment; filename=itm_probe_results.csv\n\n")
        commands.report(mdata.itm_path, 'csv', max_rows=-1,
                        use_participation_ratio=False)

    elif output_format == 'html':

        layout_args = mdata.display_options.validate_display_args(cgi_map)
        layout_id = _get_layout_id(layout_args)
        layout_filename = '%s_%s' % (query_id, layout_id)

        if not check_object(storage_path, layout_filename):
            layout_path = os.path.join(storage_path, layout_filename + '.pkl')
            commands.layout(layout_path,
                            [mdata.itm_path],
                            os.path.join(conf.graphviz_path, 'neato'),
                            **layout_args)


        tables = mdata.report_tables(layout_args)
        img_spec = mdata.display_options.image_spec(cgi_map, query_id, layout_id)
        client_state = mdata.display_options.form_settings_data(query_id)

        cvterm_form_opts = form_input_options(mdata, query_id, conf)

        jinja_env = get_jinja_env(conf)
        tmpl = jinja_env.get_template('ITMProbe/results2.html')
        res = tmpl.render(conf=conf,
                          client_state=client_state,
                          image_processors=mdata.display_options.image_processors,
                          img_spec=img_spec,
                          cvterm_opts=cvterm_form_opts,
                          warning_msgs=mdata.warning_msgs,
                          **tables)
        html_response(res)


def render_image(cgi_map, conf):

    storage_path = _get_storage_path(conf)
    query_id = vld.hash_validator('query_id', cgi_map['query_id'])
    layout_id = vld.hash_validator('layout_id', cgi_map['layout_id'])
    layout_file = '%s_%s.pkl' % (query_id, layout_id)
    layout_path = os.path.join(storage_path, layout_file)

    mdata = restore_object(storage_path, query_id)
    kwargs =  mdata.display_options.validate_display_args(cgi_map)
    kwargs.update(mdata.display_options.validate_rendering_args(cgi_map))
    kwargs.pop('neato_seed')
    kwargs.pop('neato_options')
    kwargs['out_format'] = cgi_map['image_format']
    kwargs['write_http_header'] = True

    commands.image('-', layout_path, [mdata.itm_path], **kwargs)


def standalone_run(cgi_map, conf):

    try:
        json_gz_file = StringIO(cgi_map['input_data'])
        results_gz_file = StringIO()
        input_fp = gzip.GzipFile(fileobj=json_gz_file)
        output_fp = gzip.GzipFile(fileobj=results_gz_file, mode='wb')
        commands.standalone_run(input_fp, output_fp)
        input_fp.close()
        output_fp.close()
        sys.stdout.write("Content-Type: application/x-gzip\n\n")
        sys.stdout.write(results_gz_file.getvalue())

    except:
        sys.stdout.write("Content-Type: text/plain\n\n")
        sys.stdout.write('UNRECOVERABLE ERROR\n')


VIEWS = {'0': run_www_model,
         '1': layout_www_model,
         '2': render_image,
         '4': enrich_query,
         '5': standalone_run,
         }


