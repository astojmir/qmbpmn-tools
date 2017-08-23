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

import cPickle as pickle
import numpy as np
from scipy.sparse import lil_matrix
from ..utils.dataobj import save_data_object
from .adjmatrix import CSRAdjacencyMatrix

class DirectedGraph(object):
    """
    Directed graph. Based on coo formatted sparse matrix.
    """

    _attrs = ['nodes', '_adjacency_matrix', 'node_weights']

    def __init__(self, dumpfile=None):

        self.filename = None # This is set by owner
        self.nodes = []
        self.node2index = {}
        self._num_edges = 0
        self._num_nodes = 0
        # This attribute is used to pass information about the value used for
        # normalization of edge weights when constructing transition matrices.
        # This is a 'public' attribute so it should be set by the 'outside'
        # code.
        self.node_weights = None
        self._adjacency_matrix = None

        if dumpfile is None:
            # This is a hack since we don't know the size of matrix in advance
            self._adjacency_matrix = lil_matrix((1,1), dtype='d')
            self._adjacency_matrix.rows = []
            self._adjacency_matrix.data = []
            self._adjacency_matrix._shape = (0,0)
        else:
            self._restore_attrs(self, dumpfile)
            self._update_vars()

    def __str__(self):

        lines = ["****** Directed Graph ******",
                 "Number of vertices: %d" % len(self.nodes),
                 "Number of edges: %d" % self._num_edges,
                 ""]
        return '\n'.join(lines)

    @staticmethod
    def get_diagonal_ix(adjacency_matrix):
        diagonal_ix = []
        A = adjacency_matrix
        row_start = A.indptr[0]
        for i, row_end in enumerate(A.indptr[1:]):
            cols = A.indices[row_start:row_end]
            diagonal_ix.append(row_start + np.arange(len(cols))[cols == i][0])
            row_start = row_end
        return diagonal_ix

    def weighted_adjacency_matrix(self, transpose=False):
        """
        Return the weighted adjacency matrix representation
        of the graph and the dictionary of nodes
        mapping to their indices.
        """
        A = self._adjacency_matrix.tocsr()
        if transpose:
            A = A.T.tocsr()
        A.sort_indices()
        diagonal_ix = self.get_diagonal_ix(A)

        return CSRAdjacencyMatrix(A, diagonal_ix, self.nodes, self.node2index,
                                  self.node_weights)

    def has_node(self, node):
        return node in self.node2index

    def insert_node(self, node):
        """
        Return the node mapped by p,
        inserting it if not found.
        """

        if node not in self.node2index:
            self.node2index[node] = len(self.nodes)
            self.nodes.append(node)

            # Grow sparse adjacency matrix
            self._adjacency_matrix._shape = (self._num_nodes+1, self._num_nodes+1)
            self._adjacency_matrix.rows.append([self._num_nodes])
            self._adjacency_matrix.data.append([0.0])
            self._num_nodes += 1

        return node

    def insert_edge(self, s1, s2, weight=None):
        """
        Insert a weighted directed edge (s1,s2).
        """
        p1 = self.insert_node(s1)
        p2 = self.insert_node(s2)
        i1 = self.node2index[p1]
        i2 = self.node2index[p2]

        if weight == None: weight = 1.0
        if p1 == p2: weight *= 2.0
        self._adjacency_matrix[i1,i2] += weight
        self._num_edges += 1

    def set_edge_weight(self, s1, s2, weight):
        """
        Set the weight of an existing edge (s1, s2)
        (if the edge does not exist, it is a NOOP).
        """
        if weight != 0.0:
            i1 = self.node2index[s1]
            i2 = self.node2index[s2]
            self._adjacency_matrix[i1,i2] = weight

    def get_edge_weight(self, s1, s2):
        """
        Get the weight of an existing edge.
        """
        i1 = self.node2index[s1]
        i2 = self.node2index[s2]
        return self._adjacency_matrix[i1,i2]

    def insert_undirected_edge(self, s1, s2, weight=None):
        """
        Insert weighted edges (s1,s2) and (s2,s1).
        """
        self.insert_edge(s1,s2,weight)
        self.insert_edge(s2,s1,weight)

    def outgoing_edges(self, node):
        """
        Return a list of all pairs (node2, weight) such that the weight of an
        edge (node, node2) is non-zero.
        """
        i = self.node2index[node]
        A = self._adjacency_matrix
        return [ (self.nodes[j], x)  \
                 for j, x in zip(A.rows[i], A.data[i]) \
                 if x > 0 ]

    def outgoing_edges_length(self, node):
        """
        Return a list of all pairs (node2, weight) such that the weight of an
        edge (node2, node) is non-zero.
        """
        i = self.node2index[node]
        A = self._adjacency_matrix
        return [ (self.nodes[j],1.0/x)  for j, x in zip(A.rows[i], A.data[i]) ]

    def get_edges(self):
        """
        Return all edges of the graph.
        """
        return ( (p1,p2) for p1 in self.nodes for p2, _ in self.outgoing_edges(p1) )


    def extend(self, G):
        """
        Insert all nodes and edges from a given graph.
        """
        for p1 in G.nodes:
            for p2, weight in G.outgoing_edges(p1):
                self.insert_edge(p1, p2, weight)

    def extract_nodes(self, nodes):
        """
        Construct the subgraph generated by nodes and insert its nodes and
        edges into the provided graph. If graph is None, create a new
        DirectedGraph instance.
        """

        nodes_set = set(nodes)
        G_new = DirectedGraph()
        for p1 in nodes:
            for p2, weight in self.outgoing_edges(p1):
                if p2 not in nodes_set: continue
                G_new.insert_edge(p1, p2, weight)
        return G_new


    def transitive_closure(self, nodes):
        """
        Return a set of all nodes accessible from given nodes (by following
        outgoing edges).
        """
        visited = set()
        unvisited = set(nodes)
        edges = set()

        while unvisited:
            u = unvisited.pop()
            visited.add(u)

            for v, _ in self.outgoing_edges(u):
                if v not in visited:
                    unvisited.add(v)
        return visited

    def toJSON(self, out_file):
        """
        Write a representation of this graph as CSR adjacency matrix
        to a JSON file.
        """
        A = self.weighted_adjacency_matrix().adjacency_matrix
        nw = list(self.node_weights) if self.node_weights is not None else None
        obj = {'graph': {'nodes': self.nodes,
                         'data': list(A.data),
                         'indices': list(A.indices),
                         'indptr': list(A.indptr),
                         'node_weights': nw,
                         },
               }
        save_data_object(obj, out_file)

    def _reduce(self):
        # Pickle a dictionary of values to make it easier to move or change
        # classes later
        obj_data = dict((key, getattr(self, key)) for key in self._attrs)
        return obj_data

    def tostring(self):
        """ Convert to a binary string """

        return pickle.dumps(self._reduce(), 2)

    def tofile(self, fp):
        """ Write data to a file. """

        pickle.dump(self._reduce(), fp, 2)

    def copy(self):
        """ Produce a full (deep) copy of the graph. """
        # For now implemented through pickling.
        s = self.tostring()
        return self.__class__(s)

    def _restore_attrs(self, dumpfile):

        if hasattr(dumpfile, 'read'):
            obj_data = pickle.load(dumpfile)
        elif isinstance(dumpfile, basestring):
            obj_data = pickle.loads(dumpfile)
        for key in obj_data:
            setattr(self, key, obj_data[key])

    def _update_vars(self):

        self.node2index = dict((node, i) for i, node in enumerate(self.nodes))
        self._num_nodes = len(self.nodes)
        self._num_edges = self._adjacency_matrix.nnz

