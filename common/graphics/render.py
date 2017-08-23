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

"""Rendering of graphs using Graphviz."""


from subprocess import Popen, PIPE
from cStringIO import StringIO


class GraphvizLayout(object):
    """Routines for producing and rendering Graphviz layouts."""

    def __init__(self, shown_nodes, shown_edges,
                 nodes_attr=None, default_attr=None, edges_attr=None,
                 program='neato', program_options="",
                 directed=False, graph_name='G'):

        """
        :param `shown_nodes`: list of nodes (as strings) to be displayed;
        :param `shown_edges`: list of edges (as pairs of strings) to be displayed;
        :param `nodes_attr`: dictionary of attributes for nodes. Each node maps
                             to a dictionary of attributes.
        :param `default_attr`: dictionary of default attributes. Each of
                               'graph', 'node', 'edge', maps to a dictionary of
                               attributes.
        :param `edges_attr`: dictionary of attributes for edges. Each edge maps
                             to a dictionary of attributes.
        :param `program`: Graphviz program to be used (e.g. neato, dot). Must
                          use full path if graphviz is not on the environment
                          path.
        :param `directed`: True if graph should be treated as directed.
        :param `graph_name`: a label for graph title.
        """

        self.shown_nodes = shown_nodes
        self.shown_edges = shown_edges
        self.nodes_attr = nodes_attr if nodes_attr is not None else {}
        self.default_attr = default_attr if default_attr is not None else {}
        self.edges_attr = edges_attr if edges_attr is not None else {}
        self.program = program
        self.program_options = program_options
        self.graph_name = graph_name

        if directed:
            self.edge_type = '->'
            self.graph_type = 'digraph'
        else:
            self.edge_type = '--'
            self.graph_type = 'graph'

    def write_layout_dot(self, fp):
        """Write the graph as Graphviz dot into fp."""

        fp.write('%s %s {\n' % (self.graph_type, self.graph_name))

        # Write defaults
        for kw in ['graph', 'node', 'edge']:
            if kw in self.default_attr:
                fp.write('%s [' % kw)
                for key, val in self.default_attr[kw].iteritems():
                    fp.write(' %s=%s,' % (key, val))
                fp.write(' ]\n')

        # Write nodes_attr
        for v in self.shown_nodes:
            if (v not in self.nodes_attr) or (len(self.nodes_attr[v]) ==  0):
                continue
            fp.write('"%s" [' % v)
            for item in self.nodes_attr[v].iteritems():
                fp.write(' %s=%s,' % item)
            fp.write(' ];\n')

        # Write edges
        for e in self.shown_edges:
            fp.write('"%s" %s "%s" ' % (e[0], self.edge_type, e[1]))

            if (e in self.edges_attr) and len(self.edges_attr[e]):
                fp.write('[')
                for item in self.edges_attr[e].iteritems():
                    fp.write(' %s=%s,' % item)
                fp.write(' ]')
            fp.write(';\n')

        fp.write('}\n')


    def open_pipe(self, program_options):
        """Open pipe to Graphviz program.

        Returns a pair of (fp_in, fp_out). The stream fp_in will take a file in
        dot format and fp_out will give the output (depending on
        program_options).
        """

        command = '%s %s' % (self.program, program_options)
        FNULL = open('/dev/null', 'w')
        p = Popen(command, shell=True, bufsize=0,
                  stdin=PIPE, stdout=PIPE, stderr=FNULL, close_fds=True)
        return p.stdin, p.stdout



class NeatoLayout(GraphvizLayout):
    """
    Routines for producing and rendering Graphviz neato layouts as required
    by ITMProbe.

    Works in two stages. At initialization it runs neato to obtain a full
    layoutin dot format, which it then processes. Then, the method
    write_colored_dot allows coloring the nodes while retaining the same layout.
    """

    def __init__(self, shown_nodes, shown_edges,
                 nodes_attr=None, default_attr=None, edges_attr=None,
                 program='neato', program_options="",
                 directed=False):
        """
        :param `shown_nodes`: list of nodes (as strings) to be displayed;
        :param `shown_edges`: list of edges (as pairs of strings) to be displayed;
        :param `nodes_attr`: dictionary of attributes for nodes. Each node maps
                             to a dictionary of attributes.
        :param `default_attr`: dictionary of default attributes. Each of
                               'graph', 'node', 'edge', maps to a dictionary of
                               attributes.
        :param `edges_attr`: dictionary of attributes for edges. Each edge maps
                             to a dictionary of attributes.
        :param `program`: Graphviz program to be used (e.g. neato, dot). Must
                          use full path if graphviz is not on the environment
                          path.
        :param `directed`: True if graph should be treated as directed.
        """

        super(NeatoLayout, self).__init__(shown_nodes, shown_edges,
                                          nodes_attr, default_attr, edges_attr,
                                          program, program_options, directed)

        layout_out = StringIO()
        full_options = '-Tdot %s' % program_options
        neato_in, neato_out = self.open_pipe(full_options)

        self.write_layout_dot(neato_in)
        neato_in.close()

        neato_out.next()
        for line in neato_out:
            if line.strip() != '}':
                layout_out.write(line)
        neato_out.close()
        self.dot_layout = layout_out.getvalue()


    def write_colored_dot(self, fp, nodes_attr=None, default_attr=None):
        """Write the colored dot layout into fp."""

        nodes_attr = nodes_attr if nodes_attr is not None else {}
        default_attr = default_attr if default_attr is not None else {}

        # We use the stored dot output by neato in the layout step.

        fp.write('%s G {\n' % self.graph_type)

        # Write defaults at the top - must not overlap with what is already
        # there
        for kw in ['graph', 'node', 'edge']:
            if kw in default_attr:
                fp.write('%s [' % kw)
                for key, val in default_attr[kw].iteritems():
                    fp.write(' %s=%s,' % (key, val))
                fp.write(' ];\n')

        # Write the positioning layout
        fp.write(self.dot_layout)

        # Write nodes_attr at the end - again there should be no conflict
        for v in self.shown_nodes:
            if (v not in nodes_attr) or (len(nodes_attr[v]) ==  0):
                continue
            fp.write('"%s" [' % v)
            for item in nodes_attr[v].iteritems():
                fp.write(' %s=%s,' % item)
            fp.write(' ];\n')

        fp.write('}\n')


    def save_layout(self, fp):
        """Write dot layout into fp."""

        fp.write('%s G {\n' % self.graph_type)
        fp.write(self.dot_layout)
        fp.write('}\n')

    def render_colored(self, program_options, nodes_attr=None,
                       default_attr=None):
        """
        Run neato to render the colored layout. Colors are specified through
        nodes_attr and default_attr.
        """

        nodes_attr = nodes_attr if nodes_attr is not None else {}
        default_attr = default_attr if default_attr is not None else {}

        neato_in, neato_out = self.open_pipe('-n %s' % program_options)

        self.write_colored_dot(neato_in, nodes_attr, default_attr)
        neato_in.close()

        return neato_out
