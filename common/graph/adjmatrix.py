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

class CSRAdjacencyMatrix(object):
    """
    Adjacency matrix in CSR format.

    This class stores all necessary data for ITM Probe as
    attributes:

    * adjacency_matrix - a matrix in CSR format, owned by
                         the object instance, hence can
                         be overwritten.
    * diagonal_ix - array of indices of diagonal elements.
    * nodes - list of node names.
    * node2index - mapping of node names to adjacency matrix indices.
    * row_weights - weights used to normalize rows to obtain the transition
                    matrix.
    All the above attributes except adjacency_matrix should not be modified
    in-place.
    """

    def __init__(self, adjacency_matrix, diagonal_ix, nodes, node2index,
                 row_weights=None):

        self.adjacency_matrix = adjacency_matrix
        self.diagonal_ix = diagonal_ix
        self.nodes = nodes
        self.node2index = node2index
        self.row_weights = row_weights
        if row_weights is None:
            A = self.adjacency_matrix
            self.row_weights = np.empty(len(nodes), dtype=A.data.dtype)
            row_start = A.indptr[0]
            for i, row_end in enumerate(A.indptr[1:]):
                row_data = A.data[row_start:row_end]
                self.row_weights[i] = row_data.sum()
                row_start = row_end

    def copy(self):
        """
        Create a new instance with a copy of adjacency_matrix.
        """
        A = self.adjacency_matrix.copy()
        return self.__class__(A, self.diagonal_ix, self.nodes, self.node2index,
                              self.row_weights)

    def get_df_mask(self, alpha_out=1.0, alpha_out_map=None, alpha_in=1.0,
                    alpha_in_map=None):
        """
        Construct an array of damping factors of the same size as data array of the
        adjacency_matrix.
        """

        # Construct edge modification factors
        A = self.adjacency_matrix

        df_mask = np.zeros_like(A.data)

        if alpha_in_map is None:
            alpha_in_map = {}
        if alpha_out_map is None:
            alpha_out_map = {}

        # Rows are multiplied with df_out
        tmp = alpha_out * np.ones(A.shape[0], 'd')
        for i, alpha in alpha_out_map.iteritems():
            tmp[i] = alpha

        row_start = A.indptr[0]
        for i, row_end in enumerate(A.indptr[1:]):
            df_mask[row_start:row_end] = tmp[i]
            row_start = row_end

        # ... and columns with df_in
        tmp = alpha_in * np.ones(A.shape[0], 'd')
        for j, alpha in alpha_in_map.iteritems():
            tmp[j] = alpha
        col_mask = tmp[A.indices]
        np.multiply(col_mask, df_mask, df_mask)

        return df_mask

    def make_transition_matrix(self):
        """
        Converts (in place) the adjacency matrix
        into a transition matrix - not necessarily
        stochastic as the row weights may sum to less
        than unity.
        """
        A = self.adjacency_matrix
        row_start = A.indptr[0]
        for i, row_end in enumerate(A.indptr[1:]):
            row_data = A.data[row_start:row_end]
            row_sum = self.row_weights[i]
            if row_sum > 0.0:
                # Here the implicit assumption is that self.row_weights[i] is
                # zero iff the sum of entries in row i is zero.
                np.divide(row_data, row_sum, row_data)
            row_start = row_end

