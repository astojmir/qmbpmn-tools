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
import textwrap
from ...common.graphics.colormaps import BrewerColors
from ...common.graphics.render import GraphvizLayout
from ...common.graphics import image_processors as imp


REL_COLORS = [("is_a", "black"),
              ("part_of", "blue"),
              ("regulates", "gold1"),
              ("negatively_regulates", "orangered1"),
              ("positively_regulates", "green2")]


def _find_roots(edges):
    has_outgoing_edges = {}
    for o1, _, o2 in edges:
        has_outgoing_edges[o1] = False
        if o2 not in has_outgoing_edges:
            has_outgoing_edges[o2] = True

    roots = [ t[0] for t in has_outgoing_edges.iteritems() if t[1] ]
    if len(roots) > 1:
        for p in roots:
            edges.append([p, 'is_a', 'ALL'])
        return True
    return False


def _format_and_wrap_name(name, text_wrapper):
    line_break = r'<br/>'
    formatted_name = line_break.join(text_wrapper.wrap(name))
    return formatted_name


def _dot_layout_args(edges, node_props, colorscheme='Blues8', add_root=True):

    node_fmt = '<<table border="0" href="%s" target="_blank" title="%s">' \
               '<tr><td>%s</td></tr>' \
               '<tr><td><font point-size="8.0">%s</font></td></tr>' \
               '</table>>'

    text_wrapper = textwrap.TextWrapper(width=24, break_long_words=False)

    default_attr = {'graph': {'ratio': 'auto',
                              'rankdir': '"BT"',
                              'size': '"7.0 9.0"',
                              'bgcolor': "transparent",
                              },
                    'node': {'shape': 'Mrecord',
                             'fontname': '"Arial"',
                             'fontsize': '10.0',
                             'style': 'filled',
                             'fixedsize': 'false',
                             'width': '1.0',
                             'height': '0.35',
                             'colorscheme': colorscheme,
                             'color': 'black',
                             'fillcolor': '"1"',
                             'margin': '"0.02,0.02"',
                             },
                    'edge': {'color': 'black',
                             }
                    }

    nodes = []
    nodes_attr = {}
    edges_attr = {}
    relation_attr = dict((key, {'color': color}) for key, color in REL_COLORS)

    # Introduce a special root node if there is more than one node with
    # ingoing but no outgoing edges
    if add_root:
        _find_roots(edges)

    # Compute color scale (log10 of Evalue)
    base_val = min(int(item[2]) for item in node_props if int(item[2]) > 0)
    bins = [10**-m for m in xrange(base_val, base_val+7)]

    # Generate attributes for nodes
    for item in node_props:
        term_id, name, level, term_url = item[:4]
        nodes.append(term_id)
        val = int(level) - base_val + 2
        val = 8 if val > 8 else val
        val = 1 if val < 1 else val
        fontcol = 'white' if val > 5 else 'black'
        label = node_fmt % (term_url,
                            name,
                            _format_and_wrap_name(name, text_wrapper),
                            term_id)
        nodes_attr[term_id] = {'label': label,
                               'fillcolor': '"%d"' % val,
                               'fontcolor': fontcol}

    # Generate attributes for edges from relation_attr.
    shown_edges = []
    for term_id1, rel, term_id2 in edges:
        edge = (term_id1, term_id2)
        shown_edges.append(edge)
        if (rel in relation_attr):
            edges_attr[edge] = relation_attr[rel]

    layout_kwargs = {'shown_nodes': nodes,
                     'shown_edges': shown_edges,
                     'nodes_attr': nodes_attr,
                     'default_attr': default_attr,
                     'edges_attr': edges_attr,
                     'directed': True,
                     'graph_name': 'ontology_part',
                     }


    return bins, layout_kwargs


def render_enriched_subgraph(fp_out, edges, node_props, img_format='svg',
                             dot_path='', colorscheme='Blues8'):

    nav_opts = {'script_path': 'netmap',
                'map_title': 'Term Navigator',
                'tools_title': 'TERM NAVIGATOR',
                'image_view': (620, 590),
                'mainMap_pos': (0,190),
                'mainMap_view': (620,400),
                'refMap_pos': (324,10),
                'refMap_scale': 0.4,
                'zoom_factor': 0.7,
                'zoom_levels': 10,
                'toolbar_pos': (20,40),
                'legend_pos': (20,130),
                'vertical_legend': False,
                'node_legend_pos': None,
                }

    # Map format |-> (postprocessing_class)
    frmt_map = {'svg': \
                imp.SVGOutputImage('svg','SVG',"image/svg+xml",
                                   write_http_header=False),
                'netmapsvg': \
                imp.SVGNavigatorOutputImage('SVG in Navigator',
                                            write_http_header=False,
                                            navigator_options=nav_opts),
       }


    img_proc = frmt_map[img_format]
    dot_options = '-q %s' % img_proc.neato_option
    dot_executable = os.path.join(dot_path, 'dot')

    bins, layout_kwargs = _dot_layout_args(edges, node_props, colorscheme)
    legend_items = (list(reversed(BrewerColors[colorscheme])),
                    list(reversed(bins)))

    dot_renderer = GraphvizLayout(program=dot_executable, **layout_kwargs)

    dot_in, dot_out = dot_renderer.open_pipe(dot_options)
    dot_renderer.write_layout_dot(dot_in)
    dot_in.close()

    img_proc.process_stream(dot_out, fp_out, legend_items)



def create_and_save_image(graphics_file, img_format, dot_path, colorscheme,
                          edges, node_props):
    if len(edges):
        with open(graphics_file, 'wb') as fp:
            render_enriched_subgraph(fp, edges, node_props, img_format,
                                     dot_path, colorscheme)
