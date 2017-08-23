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
import os.path
import numpy as np
from scipy.sparse import csr_matrix
from ..common.utils.dataobj import restore_data_object
from ..common.utils.pickling import save_object
from ..common.utils.pickling import restore_object
from .core.emitting import EmittingAnalysis
from .core.absorbing import AbsorbingAnalysis
from .core.nchannel import NormChannelAnalysis
from .core.laplacian import FullGraphLaplacian
from .core.script import ScriptContext
from .core.script import connect_main_db
from .output import formatted_table
from .output import print_table_funcs
from ..common.graphics.itm_graphics import make_layout
from ..common.graphics.itm_graphics import render_one_color
from ..common.graphics.itm_graphics import render_mixed_color
from ..common.graphics.itm_graphics import discretize_log_upper
from ..common.graphics.itm_graphics import discretize_linear
from ..common.graphics.itm_graphics import discretize_sqrt
from ..common.graphics import image_processors as imp
from ..common.graph.csrgraph import CSRDirectedGraph


model_classes = {'emitting': EmittingAnalysis,
                 'absorbing': AbsorbingAnalysis,
                 'normalized-channel': NormChannelAnalysis,
                 }

def graph_from_kwargs(kwargs, json_filename=None):
    """
    Constructs a graph in CSR format either by loading from file or by using
    supplied arguments.
    """

    if 'graph_path' in kwargs:
        graph_path = kwargs.pop('graph_path')
        with open(graph_path, 'rb') as fp:
            G = CSRDirectedGraph(fp)
            G.filename = graph_path

    elif 'graph' in kwargs:
        _gv = kwargs.pop('graph')
        nodes = _gv['nodes']
        A = csr_matrix((_gv['data'], _gv['indices'], _gv['indptr']),
                       shape=(len(nodes), len(nodes)),
                       dtype='float')
        G = CSRDirectedGraph(A, nodes)
        G.filename = json_filename
        if 'node_weights' in _gv:
            G.node_weights = _gv['node_weights']
    else:
        raise RuntimeError("Input graph is not specified.")

    if 'graph_name' in kwargs:
        G.name = kwargs.pop('graph_name')
    else:
        G.name = 'Custom graph'

    kwargs['G'] = G


def run(output_file, input_json_file):

    kwargs = restore_data_object(input_json_file)

    model_name = kwargs.pop('model')
    model_class = model_classes[model_name]
    graph_from_kwargs(kwargs, input_json_file)

    model = model_class(**kwargs)
    model.save(output_file)


def table(script, databases, out_format='txt'):

    tbl_params = ['data', 'column_headers', 'column_formats', 'title']
    with ScriptContext(tbl_params, databases) as cntx:
        kwargs = cntx.execute(script)

    title, column_headers, body, _ = formatted_table(**kwargs)
    print_table = print_table_funcs[out_format]
    print_table(title, column_headers, body)


def load_default_script(base_script_name, script_name):
    """ Load default script. """

    default_dir = os.path.join(os.path.dirname(__file__), 'itm_scripts')
    data = []
    for filename in (base_script_name, script_name):
        if filename is None:
            continue
        full_path = os.path.join(default_dir, '{0}.its'.format(filename))
        with open(full_path, 'rb') as fp:
            data.append(fp.read())
    return '\n'.join(data)


def get_script_vars(max_rows=40, order_by='total_content',
                    use_participation_ratio=True, cutoff_value=None):

    if use_participation_ratio:
        cutoff_value = None
    if cutoff_value is not None:
        criterion = 'WHERE %s > %.6e' % (order_by, cutoff_value)
    else:
        criterion = ''

    script_vars = {'$orderby$': order_by,
                   '$maxrows$': '%d' % max_rows,
                   '$usepr$': str(int(use_participation_ratio)),
                   '$criterion$': criterion,
                   }
    return script_vars


def report_tables(databases, show_input_params=True, show_summary=True,
                  show_nodes=True, show_excluded_nodes=False, max_rows=40,
                  order_by='total_content', use_participation_ratio=True,
                  cutoff_value=None):

    tbl_params = ['data', 'column_headers', 'column_formats', 'title']

    script_vars = get_script_vars(max_rows, order_by, use_participation_ratio,
                                  cutoff_value)

    script_params = [('params_default_script', show_input_params),
                     ('summary_default_script', show_summary),
                     ('nodes_default_script', show_nodes),
                     ]

    with ScriptContext(tbl_params, databases) as cntx:
        props = cntx.get_properties()
        tables = []

        for key, do_it in script_params:
            if do_it:
                script = load_default_script(props['base_default_script'],
                                             props[key])
                kwargs = cntx.execute(script, script_vars)
                tbl = formatted_table(**kwargs)
            else:
                tbl = None
            tables.append(tbl)
        if show_excluded_nodes:
            script = load_default_script(None, 'excluded_nodes_default')
            kwargs = cntx.execute(script, script_vars)
            tables.append(formatted_table(**kwargs))

    return tables


def report(ITM_file, out_format='txt', show_input_params=True,
           show_summary=True, show_nodes=True, max_rows=40,
           order_by='total_content', use_participation_ratio=True,
           cutoff_value=None):


    databases = [ITM_file]
    tables = report_tables(databases,
                           show_input_params=show_input_params,
                           show_summary=show_summary,
                           show_nodes=show_nodes,
                           max_rows=max_rows,
                           order_by=order_by,
                           use_participation_ratio=use_participation_ratio,
                           cutoff_value=cutoff_value)

    print_table = print_table_funcs[out_format]
    for tbl in tables:
        if tbl is not None:
            title, column_headers, body, _ = tbl
            print_table(title, column_headers, body)


def custom_layout(output_file, script, databases, neato_executable='neato',
                  neato_seed=None, script_vars=None):

    layout_params= ['shown_nodes', 'sources', 'sinks']

    with ScriptContext(layout_params, databases) as cntx:
        props = cntx.get_properties()
        if script is None:
            script = load_default_script(props['base_default_script'],
                                         props['layout_default_script'])
        kwargs = cntx.execute(script, script_vars)


    graph_file_ext = os.path.splitext(props['graph_filename'])[1]
    if graph_file_ext == '.json':
        graph_kwargs = restore_data_object(props['graph_filename'])
    elif graph_file_ext == '.pkl':
        graph_kwargs = {'graph_path': props['graph_filename']}
    else:
        raise RuntimeError("Invalid graph filename extension")
    graph_from_kwargs(graph_kwargs)
    G = graph_kwargs['G']

    shown_nodes = [row[0] for row in kwargs['shown_nodes']]
    sources = [row[0] for row in kwargs['sources']]
    sinks = [row[0] for row in kwargs['sinks']]
    layout = make_layout(G, shown_nodes, sources, sinks,
                         neato_executable, neato_seed)
    save_object(layout, '', output_file, '')


def layout(output_file, databases, neato_executable='neato',
           neato_seed=None, max_rows=40, order_by='total_content',
           use_participation_ratio=True, cutoff_value=None):

    script_vars = get_script_vars(max_rows, order_by, use_participation_ratio,
                                  cutoff_value)
    custom_layout(output_file, None, databases, neato_executable, neato_seed,
                  script_vars)


def custom_image(output_file, layout_file, script, databases,
                 colormap='Blues8', out_format='svg',
                 script_vars=None, mixed_colors=False,
                 bins_func=discretize_linear(8),
                 write_http_header=False):

    img_proc = imp.IMG_PROC_MAP[out_format]
    img_proc.write_http_header = write_http_header
    layout = restore_object('', layout_file, '')
    node2index = dict((p, i) for i, p in enumerate(layout.shown_nodes))

    with ScriptContext(['node_values', 'bins'], databases) as cntx:
        cntx.create_function('bin', 1, bins_func)
        if script is None:
            props = cntx.get_properties()
            if mixed_colors:
                script = load_default_script(props['base_default_script'],
                                             'mixed_colors_image_default')
            else:
                script = load_default_script(props['base_default_script'],
                                             'one_color_image_default')

        kwargs = cntx.execute(script, script_vars)

    # Bins are used by both one_color and mixed_colors rendering routines
    bins = np.zeros(len(kwargs['bins']), dtype='d')
    for i, row in enumerate(kwargs['bins']):
        bins[i] = row[0]

    if mixed_colors:
        node_values = np.zeros((len(layout.shown_nodes), 3), dtype='d')
        for row in kwargs['node_values']:
            node = row[0]
            num_cols = min(3, len(row)-1)
            if node in node2index:
                i = node2index[node]
                for j in xrange(num_cols):
                    node_values[i, j] = row[j+1]

        neato_out, legend_items = render_mixed_color(layout,
                                                     img_proc.neato_option,
                                                     node_values, bins)
    else: # one color only
        node_values = np.zeros(len(layout.shown_nodes), dtype='d')
        for row in kwargs['node_values']:
            node = row[0]
            if node in node2index:
                node_values[node2index[node]] = row[1]
        neato_out, legend_items = render_one_color(layout,
                                                   img_proc.neato_option,
                                                   node_values, bins, colormap)

    if output_file == '-':
        img_proc.process_stream(neato_out, sys.stdout, legend_items)
    else:
        with open(output_file, 'wb') as fp:
            img_proc.process_stream(neato_out, fp, legend_items)


def image(output_file, layout_file, databases, colormap='Blues8',
          out_format='svg', mixed_colors=False, value_cols=None,
          max_rows=40, order_by='total_content', use_participation_ratio=True,
          cutoff_value=None, bins_func='linear', write_http_header=False):


    num_bins = 256 if mixed_colors else 8
    _bins_functions = {'log_upper': discretize_log_upper(num_bins),
                       'linear': discretize_linear(num_bins),
                       'sqrt': discretize_sqrt(num_bins),
                       }
    _bins_func = _bins_functions[bins_func]

    script_vars = get_script_vars(max_rows, order_by, use_participation_ratio,
                                  cutoff_value)
    if value_cols is None:
        if mixed_colors:
            value_cols = "SELECT group_concat(colid) FROM datacols"
        else:
            value_cols = "SELECT '%s'" % order_by
    else:
        value_cols = "SELECT '%s'" % value_cols
    script_vars['$valcolstmt$'] = value_cols

    custom_image(output_file, layout_file, None, databases,
                 colormap, out_format, script_vars, mixed_colors,
                 _bins_func, write_http_header)


def get_saddlesum_weights(databases, value_col):

    script_vars = get_script_vars(max_rows=-1,
                                  order_by='total_content',
                                  use_participation_ratio=False,
                                  cutoff_value=None)
    script_vars['$valcol$'] = value_col

    with ScriptContext(['weights'], databases) as cntx:
        props = cntx.get_properties()
        script = load_default_script(props['base_default_script'],
                                     'saddlesum_weights_default')
        kwargs = cntx.execute(script, script_vars)

    raw_weights = [(row[0], row[1]) for row in kwargs['weights']]
    return raw_weights


def weights(databases, value_col):

    raw_weights = get_saddlesum_weights(databases, value_col)
    body = [(name, '{0:.6g}'.format(val)) for name, val in raw_weights]
    print_table = print_table_funcs['tab']
    print_table(None, None, body)


def standalone_run(input_json_file, out_fp=sys.stdout):

    conn = connect_main_db(':memory:')

    kwargs = restore_data_object(input_json_file)
    model_name = kwargs.pop('model')
    model_class = model_classes[model_name]
    graph_from_kwargs(kwargs, None)

    model = model_class(**kwargs)
    model.save(conn)

    tables = report_tables([conn], max_rows=-1, use_participation_ratio=False,
                           show_excluded_nodes=True)

    print_table = print_table_funcs['tab']
    for tbl in tables:
        if tbl is not None:
            title, column_headers, body, _ = tbl
            print_table(title, column_headers, body, fp=out_fp)

    conn.close()


def batch_run(input_json_file):

    # global_params - used to construct full graph laplacian
    #   - graph, df, antisink_map
    # Each query must specify output filename

    kwargs = restore_data_object(input_json_file)

    # Construct a full graph laplacian from global parameters
    global_params = kwargs['global_params']
    df = global_params['df']
    antisink_map = global_params['antisink_map']
    graph_from_kwargs(global_params)
    G = global_params['G']

    W = G.weighted_adjacency_matrix()
    alpha_out_map = dict( (G.node2index[p], antisink_map[p]) \
                          for p in antisink_map if G.has_node(p) )
    df_mask = W.get_df_mask(df, alpha_out_map, 1.0, None)
    SPL = FullGraphLaplacian(W, df_mask)

    for job_data in kwargs['jobs']:

        job_kwargs = {'context_laplacian': SPL}
        output_file = job_data.pop('output_file')
        model_name = job_data.pop('model')
        job_kwargs.update(job_data)
        job_kwargs['G'] = G
        job_kwargs['df'] = df

        model_class = model_classes[model_name]
        model = model_class(**job_kwargs)
        model.save(output_file)

