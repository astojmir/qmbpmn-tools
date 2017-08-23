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

from .digraph import DirectedGraph
from .adjmatrix import CSRAdjacencyMatrix
from ..utils.filesys import write_string_list
from ..utils.filesys import read_string_list


class CSRDirectedGraph(DirectedGraph):
    """
    Read-only graph in compressed format.

    This can be instantiated in several ways:

        CSRDirectedGraph(adjacency_matrix, nodes)
            with a sparse adjacency matrix and a corresponding list of nodes

        CSRDirectedGraph(s)
            with a binary string containing all data

        CSRDirectedGraph(fp)
            with an open file containing all data
    """

    _attrs = ['nodes', '_adjacency_matrix', '_diagonal_ix', 'node_weights']

    def __init__(self, *args):

        self.filename = None # This is set by owner
        self.nodes = None
        self.node2index = None
        self._num_edges = 0
        self._num_nodes = 0
        self.node_weights = None
        self._adjacency_matrix = None
        self._diagonal_ix = None

        _error = True

        if len(args) == 2:
            adjacency_matrix, nodes = args
            self.nodes = nodes
            self._adjacency_matrix = adjacency_matrix.tocsr()
            self._adjacency_matrix.sort_indices()
            self._diagonal_ix = self.get_diagonal_ix(self._adjacency_matrix)
            _error = False

        elif len(args) == 1:
            self._restore_attrs(args[0])
            _error = False

        if _error:
            raise ValueError("Unrecognized CSRDirectedGraph constructor usage")

        self._update_vars()

    def weighted_adjacency_matrix(self, transpose=False):
        """
        Return the weighted adjacency matrix representation
        of the graph and the dictionary of nodes
        mapping to their indices.
        """
        if transpose:
            A = self._adjacency_matrix.T.tocsr()
            A.sort_indices()
            diagonal_ix = self.get_diagonal_ix(A)
        else:
            A = self._adjacency_matrix.copy()
            diagonal_ix = self._diagonal_ix
        return CSRAdjacencyMatrix(A, diagonal_ix, self.nodes, self.node2index,
                                  self.node_weights)

    def outgoing_edges(self, node):

        i = self.node2index[node]
        A = self._adjacency_matrix
        rng = slice(A.indptr[i], A.indptr[i+1])
        return [ (self.nodes[j], x)  \
                 for j, x in zip(A.indices[rng], A.data[rng]) \
                 if x > 0]

    def insert_node(self, p):
        raise NotImplementedError('May not add nodes or edges to CSRDirectedGraph instance.')

    def insert_edge(self, s1, s2, weight=None):
        raise NotImplementedError('May not add nodes or edges to CSRDirectedGraph instance.')

    def extend(self, G):
        raise NotImplementedError('May not add nodes or edges to CSRDirectedGraph instance.')

