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

import numpy as np
from collections import defaultdict
from .colormaps import BrewerColors
from .render import NeatoLayout

MIN_BRIGHTNESS = 0.3

# Discretization function factories for color imaging
def discretize_log_upper(num_bins, b=0.0, step=0.8, base=2.0):
    """Logarithmic discretization"""
    a = 1.0 * b - step * num_bins
    return lambda k:  pow(base, a + step * k)


def discretize_linear(num_bins, a=0.0, b=1.0):
    """Linear discretization"""
    step = (1.0 * b - a) / num_bins
    return lambda k: a + step * k


def discretize_sqrt(num_bins, a=0.0, b=1.0):
    """Square root discretization"""
    step = (1.0 * b - a) / num_bins
    return lambda k: pow(a + step * k, 2.0)


def make_layout(G, shown_nodes, sources, sinks, neato_executable='neato',
                neato_seed=None):
    """
    Produce a layout of a subgraph using Graphviz.
    """

    nodes_attr = defaultdict(dict)
    edges_map = {}

    # Extract edges: need to check if directed.
    for v1 in shown_nodes:
        if G.has_node(v1):
            for v2, wght in G.outgoing_edges(v1):
                if v2 not in shown_nodes:
                    continue
                # Vertices with self-pointing edges have a different shape
                if v1 == v2:
                    if wght > 0.0:
                        nodes_attr[v1] = {'shape': 'ellipse',
                                          'height': 0.20,
                                          'width': 0.04 + 0.08 * len(v1.__str__()),
                                          }
                elif (v2, v1) in edges_map:
                    # undirected edge
                    edges_map[(v2, v1)] = False
                else:
                    # directed edge
                    edges_map[(v1, v2)] = True

    shown_edges = sorted(edges_map.keys())
    edges_attr = {}.fromkeys((e for e in edges_map if edges_map[e]),
                             {'dir': 'forward'})

    # Default attributes
    default_attr = {'graph': {'pack': 'true',
                              'overlap': 'true',
                              'outputorder': '"edgesfirst"',
                              },
                    'node': {'shape': 'box',
                             'fontsize': '7',
                             'width': '0.34',
                             'height': '0.16',
                             'style': 'filled',
                             'fixedsize': 'true',
                             },
                    'edge': {'len': '0.9',
                             }
                    }

    # Update node widths
    for node in shown_nodes:
        nodes_attr[node]['width'] = 0.02 + 0.08 * len(node.__str__())

    # Sources are hexagons
    for src in sources:
        if src in shown_nodes:
            nodes_attr[src].update({'shape': 'hexagon',
                                    'height': 0.35,
                                    'width': 0.08 + 0.08 * len(src.__str__()),
                                    })

    # Sinks are octagons
    for snk in sinks:
        if snk in shown_nodes:
            nodes_attr[snk].update({'shape': 'octagon',
                                    'height': 0.35,
                                    'width': 0.08 + 0.08 * len(snk.__str__()),
                                    })

    # Apply neato seed if given
    if neato_seed is None:
        neato_options = '-Gstart=random'
    else:
        neato_options = '-Gstart=%d' % neato_seed

    return NeatoLayout(shown_nodes, shown_edges,
                       nodes_attr, default_attr,
                       edges_attr, neato_executable,
                       neato_options)


def render_one_color(ITM_layout, neato_options, node_values, bins, colormap):


    nodes_attr = defaultdict(dict)
    default_attr = {'graph': {'bgcolor': 'transparent',
                              },
                    'node': {'fontcolor': '"#000000"',
                             'fontname': '"Helvetica"',
                             'color': '"#606060"',
                             'colorscheme': colormap,
                             },
                    'edge': {'color': '"#606060"',
                             'arrowsize': '0.5'
                             }
                    }
    color_list = BrewerColors[colormap]
    color_brightness = np.array(color_list).mean(1) / 256
    node_color_ixs = np.digitize(node_values, bins)
    node_dark = color_brightness[node_color_ixs] < MIN_BRIGHTNESS

    for i, node in enumerate(ITM_layout.shown_nodes):
        nodes_attr[node]['fillcolor'] = '%d' % (1 + node_color_ixs[i])

        # Fix fontcolor of nodes that have too dark fillcolor
        if node_dark[i]:
            nodes_attr[node]['fontcolor'] = '"#ffffff"'

    # Prepare legend
    legend_items = (color_list, bins)

    fp_out = ITM_layout.render_colored(neato_options, nodes_attr, default_attr)
    return fp_out, legend_items


def render_mixed_color(ITM_layout, neato_options, node_values, bins):

    nodes_attr = defaultdict(dict)
    default_attr = {'graph': {'bgcolor': 'transparent',
                              },
                    'node': {'fontcolor': '"#000000"',
                             'fontname': '"Helvetica"',
                             'color': '"#606060"',
                             },
                    'edge': {'color': '"#606060"',
                             'arrowsize': '0.5'
                             }
                    }

    Z = np.zeros(node_values.shape, dtype='int')
    for j in xrange(Z.shape[1]):
        Z[:,j] = 255 - np.digitize(node_values[:,j], bins)

    if Z.shape[1] == 1:
        picker = lambda i: (Z[i, 0], 255, 255)
    elif Z.shape[1] == 2:
        picker = lambda i: (Z[i, 0], 255, Z[i, 1])
    elif Z.shape[1] >= 3:
        picker = lambda i: (Z[i, 0], Z[i, 2], Z[i, 1])

    for i, node in enumerate(ITM_layout.shown_nodes):
        rgb_color = picker(i)
        hexcolor = '"#%.2x%.2x%.2x"' % rgb_color
        nodes_attr[node]['fillcolor'] = hexcolor

        # Fix fontcolor of nodes that have too dark fillcolor
        brightness = sum(rgb_color) / 3.0 / 256
        if brightness < MIN_BRIGHTNESS:
            nodes_attr[node]['fontcolor'] = '"#ffffff"'

    fp_out = ITM_layout.render_colored(neato_options, nodes_attr,
                                       default_attr)
    return fp_out, None
