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
from . import BasicITM
from .laplacian import BasicLaplacian
from ...common.utils.newton import rootfind_newton

def evaluate_context(SPL, source_ixs):

    H = np.zeros((SPL.L.shape[0],len(source_ixs)), 'd')
    for j, s in enumerate(source_ixs):
        H[:,j] = SPL.solve(SPL.get_boundary_row(s), False)
        H[source_ixs,j] = 0.0
        H[s,j] = 1.0
    return H

def _process_context_SPL(source_ixs, SPL):
    SPL.set_boundary_ixs(source_ixs)
    return evaluate_context(SPL, source_ixs)

def _process_context_df(W, source_ixs, alpha_out_map, df):

    if df > (1.0 - 1e-3):
        raise RuntimeError('Cannot evaluate a context with a damping factor'
                           ' too close to 1.')
    df_mask = W.get_df_mask(df, alpha_out_map, 1.0, None)
    SPL = BasicLaplacian(W, df_mask, boundary_rows=source_ixs)
    return evaluate_context(SPL, source_ixs)


def _process_context_mu_newton(W,
                               source_ixs,
                               alpha_out_map,
                               target_avg_path_length,
                               maxiter=50,
                               tol=1.0e-11):

    # Check if target_path_length >= 1
    if target_avg_path_length < 1.0:
        raise RuntimeError("Path length for emitting mode cannot"
                           " be smaller than 1.")

    # Check if target_path_length > n
    if target_avg_path_length > len(W.nodes):
        target_avg_path_length = len(W.nodes)

    # Dummy df_mask - renormalized later so the exact choice of damping
    # factor is not important
    df_mask = W.get_df_mask(0.85, alpha_out_map, 1.0, None)

    def _root_func(x0):
        df_mask1 = x0 * df_mask / df_mask.max()
        SPL = BasicLaplacian(W.copy(), df_mask1, boundary_rows=source_ixs)
        v = np.ones(SPL.L.shape[0], dtype='d')
        v[source_ixs] = 0.0
        G_row_sum = SPL.solve(v, True)
        H_row_sum = np.dot(SPL.boundary_row_data, G_row_sum)
        Gsq_row_sum = SPL.solve(G_row_sum, True)
        HG_row_sum = np.dot(SPL.boundary_row_data, Gsq_row_sum)
        m = len(source_ixs)

        fval = H_row_sum.sum() / m - target_avg_path_length
        fpval = HG_row_sum.sum() / m / x0

        return fval, fpval, SPL

    a = 0.0   # lower bound for df
    b = 1.0   # upper bound for df - see comment below
    x0 = 0.8  # starting guess

    # There are two cases to be considered w.r.t. upper bound:
    #
    # 1. (\I - P_{TT}) is not invertible for mu = 1.0
    #       In this case the path length is not bounded. We should be OK
    #       with Newton's method as long as we don't get to close to mu=1.0.
    #
    # 2. (\I - P_{TT}) is invertible for mu = 1.0
    #       In this case the path length is bounded and its upper bound is
    #       the value at mu = 1.0. target_avg_path_length may be larger
    #       than this value but our value will converge to 1.0 through the
    #       bisection case. It may be slow but eventually we will return a
    #       value very close to 1.0 with path length close to maximal
    #       possible.

    x, _, _, SPL =  rootfind_newton(_root_func, x0, a, b, maxiter, tol)

    if x > (1.0 - 1e-3):
        raise RuntimeError('The damping factor found is too close to 1 leading '
                           'to numerical instability.')

    H = evaluate_context(SPL, source_ixs)
    return x, H



class EmittingAnalysis(BasicITM):

    short_desc = 'Emitting model'
    base_default_script = 'emitting_base_default'
    summary_default_script = 'emitting_summary_default'
    nodes_default_script = 'emitting_nodes_default'
    layout_default_script = 'emitting_layout_default'
    mode = 'emitting'

    def __init__(self, G, source_nodes, df=1.0, antisink_map=None, da=None,
                 context_laplacian=None, **kwargs):

        if df is None and da is None:
            raise RuntimeError('Invalid specification of dissipation.')

        if antisink_map is None:
            antisink_map = dict()

        excluded_nodes = [node for node in antisink_map
                          if G.has_node(node) and antisink_map[node] == 0.0]

        super(EmittingAnalysis, self).__init__(G, excluded_nodes, source_nodes,
                                               [], **kwargs)

        self.df = df
        self.da = da

        self._solve_boundary_problem(G, antisink_map, context_laplacian)

    def _solve_boundary_problem(self, G, antisink_map, SPL=None):

        source_ixs = [G.node2index[node] for node in self.source_nodes]

        if SPL is not None:
            # Use the laplacian provided - no need to recreate it.
            self.H = _process_context_SPL(source_ixs, SPL)

        else:
            W = G.weighted_adjacency_matrix()
            alpha_out_map = dict( (G.node2index[p], antisink_map[p]) \
                                  for p in antisink_map if G.has_node(p) )

            if self.df is None:
                self.df, self.H = _process_context_mu_newton(W,
                                                             source_ixs,
                                                             alpha_out_map,
                                                             self.da)
            else:
                self.H = _process_context_df(W,
                                             source_ixs,
                                             alpha_out_map,
                                             self.df)

    def report_contexts(self):
        return [ 'Context: [%s] (Dissipation=%.2g)' % \
                 (', '.join(map(str,self.source_nodes)),
                  1.0-self.df) ]

    def _save_mode(self, conn):

        cur = conn.cursor()

        sql_insert_damping = self.db_insert_stmt('damping', 3)
        cur.execute(sql_insert_damping, (None, self.df, 1.0))

        _items = ((self.node2index[node], 0.0, 1.0) \
                  for node in self.excluded_nodes)
        cur.executemany(sql_insert_damping, _items)

        _items = ((i, self.node2index[node], 1.0) \
                  for i, node in enumerate(self.source_nodes))
        cur.executemany(self.db_insert_stmt('sources', 3), _items)

        _items = ((s, i, self.H[i,s]) for i in xrange(self.H.shape[0]) \
                                      for s in xrange(self.H.shape[1]))
        cur.executemany(self.db_insert_stmt('H', 3), _items)

        cur.close()



