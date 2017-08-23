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

"""Routines and classes for solving discrete Laplace equation."""
import numpy
from scipy import linalg
from scipy.sparse.linalg import dsolve

# Use UMFPACK if possible. SuperLU seems slower under first impression but I
# did not thoroughly test.
dsolve.use_solver(useUmfpack=True, assumeSortedIndices=True)


class BasicLaplacian(object):
    """
    Constructs the discrete Laplacian corresponding to the given adjacency
    matrix of a graph (normalized to a stochastic matrix) in a sparse form, with
    the boundary specified at the construction time.
    Precomputes the inverse of the Laplacian (Green's function) as a sparse
    LU-decomposition using a direct linear solver (UMFPACK or SuperLU). The
    inverse is accessed using the solve() method.

    Arguments:
      * W: graph adjacency matrix storage class instance;
      * df_mask: an array of the same size as data array of
          adjacency_matrix. Should contain the damping factors that multiply
          each entry of the normalized adjacency_matrix to obtain the Markov chain
          transisiton matrix (with implicit boundary unless df_mask == 1.0).
      * boundary_rows: indices of the rows of the transisiton matrix that are
          extracted, saved and zeroed in the matrix. The extracted rows can be
          accessed using the method get_boundary_row();
      * boundary_cols: indices of the columns of the transisiton matrix that are
          extracted, saved and zeroed in the matrix. The extracted columns can be
          accessed using the method get_boundary_col();
    """

    def __init__(self, W, df_mask, boundary_rows=None, boundary_cols=None):

        # self.L will point to W.adjacency_matrix, which will be modified
        # in-place
        self.L = W.adjacency_matrix
        # This is probably unnecessary as the indices are already sorted when
        # W is created.
        self.L.sort_indices()

        self.boundary_rows = boundary_rows
        self.boundary_cols = boundary_cols

        # Construct transition matrix from adjacency. This matrix need not be
        # stochastic if W.row_weights is not set to row sums.
        W.make_transition_matrix()

        # Apply df_mask
        numpy.multiply(df_mask, self.L.data, self.L.data)

        # Extract boundaries, set them to 0.0
        self._extract_boundary()

        # Make final Laplacian operator
        numpy.multiply(-1.0, self.L.data, self.L.data)
        self.L.data[W.diagonal_ix] += 1.0

        # Solvers for computing a solution - set only on first run
        self.solve_left = None
        self.solve_right = None

    def _extract_boundary(self):

        if self.boundary_rows is None:
            self.boundary_rows = []
            self.boundary_row_data = None
        else:
            # Extract rows
            self.boundary_row_data = \
              numpy.zeros((len(self.boundary_rows), self.L.shape[1]), 'd')
            for k, i in enumerate(self.boundary_rows):
                row_data = self.L.data[self.L.indptr[i]:self.L.indptr[i+1]]
                cols = self.L.indices[self.L.indptr[i]:self.L.indptr[i+1]]
                self.boundary_row_data[k, cols] = row_data

        if self.boundary_cols is None:
            self.boundary_cols = []
            self.boundary_col_data = None
            self.boundary_row_map = {}
            self.boundary_col_map = {}
        else:
            # Extract cols
            self.boundary_col_data = \
              numpy.zeros((self.L.shape[0], len(self.boundary_cols)), 'd')
            for k, j in enumerate(self.boundary_cols):
                colinds = numpy.arange(len(self.L.indices))[self.L.indices == j]

                # This is taken from scipy method rowcol which is now
                # depreciated. It assumes sorted indices.
                # rows = [self.L.rowcol(ci)[0] for ci in colinds]
                rows = [numpy.searchsorted(self.L.indptr, ci+1)-1 \
                        for ci in colinds]
                self.boundary_col_data[rows, k] = self.L.data[colinds]

        # Zero all rows and cols corresponding to boundary indexes
        for i in self.boundary_rows + self.boundary_cols:
            self.L.data[self.L.indptr[i]:self.L.indptr[i+1]] = 0.0
            colinds = numpy.arange(len(self.L.indices))[self.L.indices == i]
            self.L.data[colinds] = 0.0

        # Boundary row and col maps
        self.boundary_row_map = dict(zip(self.boundary_rows,
                                         range(len(self.boundary_rows))))
        self.boundary_col_map = dict(zip(self.boundary_cols,
                                         range(len(self.boundary_cols))))


    def get_boundary_row(self, i):
        """
        Returns the row i (if extracted) of the original transition
        matrix.
        """

        return self.boundary_row_data[self.boundary_row_map[i], :]

    def get_boundary_col(self, j):
        """
        Returns the column j (if extracted) of the original transition
        matrix.
        """

        return self.boundary_col_data[:, self.boundary_col_map[j]]

    def get_full_greens_func(self):
        """
        Retrieve the full Green's function matrix in dense form.
        """

        greens_func = numpy.eye(self.L.shape[0], dtype='d')
        for j in xrange(self.L.shape[1]):
            x = self.solve(greens_func[:, j], True)
            greens_func[:, j] = x
        return greens_func

    def solve(self, rhs, autoTranspose=False):
        """
        If autoTranspose == False, solves the system of equations
          L^Tx = rhs, otherwise solves the system Lx = rhs. Here L denotes the
          discrete Laplacian matrix with the boundary row and column vectors
          extracted.
        """
        # Both UMFPACK and SuperLU internally use CSC format, while L uses CSR
        # format. Thus, passing L's data `as is' into those routines would give
        # us the solution to L^Tx = rhs. When autoTranspose is set to True, we
        # first have to convert L to CSR and then pass it on. We will use _left
        # to label the structures for solving L^Tx = rhs (since x multiplies L
        # on the left) and right for those that enable solving Lx = rhs (since
        # x in this case multiplies L on the right). Thus, autoTranspose set
        # really means that `left' structures are used.

        if not autoTranspose:
            if self.solve_left is None:
                A = self.L.transpose() # a CSC matrix - no copy
                self.solve_left = dsolve.factorized(A)
            solve = self.solve_left
        else:
            if self.solve_right is None:
                A = self.L.tocsc() # requires a copy
                self.solve_right = dsolve.factorized(A)
            solve = self.solve_right
        x = solve(rhs)
        return x


class FullGraphLaplacian(BasicLaplacian):
    """
    Constructs the discrete Laplacian corresponding to the given adjacency
    matrix of a graph (normalized to a stochastic matrix) in a sparse form.
    Precomputes the inverse of the Laplacian (Green's function) as a sparse
    LU-decomposition using a direct linear solver (UMFPACK or SuperLU). The
    inverse is accessed using the solve() method.

    The boundary is specified after construction (using the set_boundary_ixs()
    method), allowing the reuse of the same precomputed solution for all
    boundaries.

    Arguments:
      * adjacency_matrix: graph adjacency matrix in CSR sparse format. The
          diagonal entries MUST be present, even if zeros;
      * diagonal_ix: indices of the diagonal entries in the adjacency CSR
          matrix;
      * df_mask: an array of the same size as data array of
          adjacency_matrix. Should contain the damping factors that multiply
          each entry of the normalized adjacency_matrix to obtain the Markov chain
          transisiton matrix (with implicit boundary unless df_mask == 1.0).
    """

    #  The idea behind this is to compute the Green's function of the whole
    #  graph (which exists provided there is dissipation at every node) and then
    #  extract the solutions to the cases with boundaries using algebraic
    #  manipulations.
    #
    #  Let M = matrix([[A, B], [C, D]]) in block form and suppose we require
    #  inv(A). If we write inv(M) = matrix([[X, Y], [Z, W]]), it can be shown
    #  that  inv(A) = X - Y * inv(W) * Z. Therefore, we can obtain inv(A) by
    #  computing inv(M) (once for all boundaries) and inv(W) (once for each
    #  boundary). This may be significantly faster that computing inv(A) each
    #  time if the boundary is small and there are a lot of cases
    #  involved. Note that there are permutation matrices involved for each
    #  different set of boundary indices but they can be avoided by
    #  consideration of the maps involved.
    #
    #  In the method solve(), we are computing inv(A)*u, where u is the rhs
    #  vector, or the transpose problem. To do so efficiently, note that
    #  inv(M)*vector([u, 0]) = vector(X*u, Z*u). Hence, we use a direct solver
    #  to get vector([X*u, Z*u]) and the matrices Y and W. Then we compute
    #  inv(A)*u = X*u - (Y * inv(W)) * Z * u. The transpose problem turns out
    #  only to require dealing with inv(M).T rather than inv(M).

    def __init__(self, W, df_mask):

        super(FullGraphLaplacian, self).__init__(W, df_mask)
        self.df_mask = df_mask

    def _extract_boundary(self):
        # This function is unnecessary is this class.
        pass

    def get_boundary_row(self, i):
        """
        Returns the row i of the original transition matrix.
        """

        data = numpy.zeros(self.L.shape[1], 'd')
        sparse_row_data = self.L.data[self.L.indptr[i]:self.L.indptr[i+1]]
        cols = self.L.indices[self.L.indptr[i]:self.L.indptr[i+1]]
        data[cols] = -sparse_row_data
        data[i] += 1.0
        return data

    def get_boundary_col(self, j):
        """
        Returns the column j of the original transition matrix.
        """

        data = numpy.zeros(self.L.shape[0], 'd')
        colinds = numpy.arange(len(self.L.indices))[self.L.indices == j]
        # This is taken from scipy method rowcol which is now depreciated.
        # It assumes sorted indices.
        # rows = [self.L.rowcol(ci)[0] for ci in colinds]
        rows = [numpy.searchsorted(self.L.indptr, ci+1)-1 for ci in colinds]
        data[rows] = -self.L.data[colinds]
        data[j] += 1.0
        return data


    def solve(self, rhs, autoTranspose=False):
        """
        If autoTranspose == False, solves the system of equations
          L^Tx = rhs, otherwise solves the system Lx = rhs. Here L denotes the
          discrete Laplacian matrix with the boundary specified in a previous
          call to the set_boundary_ixs() method.
        """

        # Here symbollically (i.e. after considering permutations and
        # orderings),
        # u = rhs
        # x = X*u
        # z = Z*u
        # YQ = Y*inv(W)

        if autoTranspose:
            YQ = self.tmp_mat_T
        else:
            YQ = self.tmp_mat

        x = super(FullGraphLaplacian, self).solve(rhs, autoTranspose)
        z = x[self.boundary_ixs]
        x[self.boundary_ixs] = 0.0
        res = x - numpy.dot(YQ, z)

        return res

    def set_boundary_ixs(self, boundary_ixs):
        """
        Sets the indices of boundary entries for use in the solve() method. This
        is equivalent to zeroing the rows and columns of the Laplacian indexed
        by boundary_ixs.
        """

        self.boundary_ixs = boundary_ixs
        self.tmp_mat = self._compute_tmp_mat(boundary_ixs, False)
        self.tmp_mat_T = self._compute_tmp_mat(boundary_ixs, True)

    def _compute_tmp_mat(self, boundary_ixs, autoTranspose=False):

        # Here we extract the columns of the Green's function associated with
        # the boundary. The rows corresponding to the boundary indices are
        # extracted into the W matrix and zeroed in the original matrix.

        num_bndr = len(boundary_ixs)
        Y = numpy.zeros((self.L.shape[0], num_bndr), 'd')
        tmp = numpy.zeros(self.L.shape[0], 'd')
        for i, k in enumerate(boundary_ixs):
            tmp[:] = 0.0
            tmp[k] = 1.0
            Y[:, i] = super(FullGraphLaplacian, self).solve(tmp, autoTranspose)

        W = Y[boundary_ixs, :]
        Y[boundary_ixs, :] = 0.0
        YQ = numpy.dot(Y, linalg.inv(W))

        return YQ

    @property
    def boundary_row_data(self):
        data = numpy.zeros((len(self.boundary_ixs), self.L.shape[1]), 'd')
        for k, i in enumerate(self.boundary_ixs):
            data[k, :] = self.get_boundary_row(i)
        return data

    @property
    def boundary_col_data(self):
        data = numpy.zeros((self.L.shape[0], len(self.boundary_ixs)), 'd')
        for k, j in enumerate(self.boundary_ixs):
            data[:, k] = self.get_boundary_col(j)
        return data
