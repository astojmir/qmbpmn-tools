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


def evaluate_context(SPL, sink_ixs):

    F = np.zeros((SPL.L.shape[0],len(sink_ixs)), 'd')
    for i, k in enumerate(sink_ixs):
        F[:,i] = SPL.solve(SPL.boundary_col_data[:,i], True)
        F[sink_ixs,i] = 0.0
        F[k,i] = 1.0
    return F


def _get_disconnected_ixs(W, sink_ixs, alpha_out_map):
    # Extract the connected component of sinks in order to have the
    # solution - we set df to almost 1.0 and see what transient points have
    # positive F values
    #
    # TO DO: a better algorithm, maybe pure graph depth- or breadth- first
    # search

    epsilon = 1e-16
    df_mask = W.get_df_mask(0.9999, alpha_out_map, 1.0, None)
    SPL = BasicLaplacian(W.copy(),
                         df_mask.copy(),
                         boundary_cols=sink_ixs)
    F_row_sum = SPL.solve(SPL.boundary_col_data.sum(1), True)
    disconnected_ixs = np.arange(len(F_row_sum))[F_row_sum < epsilon]
    return list(disconnected_ixs)


def _process_context_SPL(sink_ixs, SPL):
    SPL.set_boundary_ixs(sink_ixs)
    return evaluate_context(SPL, sink_ixs)


def _process_context_df(W, sink_ixs, alpha_out_map, df):

    disconnected_ixs = [] if df <= (1.0 - 1e-14) else \
                       _get_disconnected_ixs(W, sink_ixs, alpha_out_map)
    alpha_in_map2 = {}.fromkeys(disconnected_ixs, 0.0)
    alpha_out_map2 = dict(alpha_out_map)
    alpha_out_map2.update(alpha_in_map2)

    df_mask = W.get_df_mask(df, alpha_out_map2, 1.0, alpha_in_map2)
    SPL = BasicLaplacian(W, df_mask, boundary_cols=sink_ixs)
    return evaluate_context(SPL, sink_ixs)


def _process_context_mu_newton(W,
                               sink_ixs,
                               alpha_out_map,
                               target_absorption_prob,
                               maxiter=50,
                               tol=1.0e-11):

    if not (0.0 <= target_absorption_prob <= 1.0):
        raise RuntimeError("Absorption probability must be between "
                           "0 and 1.")

    # Find n - number of nodes connected to sinks.
    disconnected_ixs = _get_disconnected_ixs(W, sink_ixs, alpha_out_map)
    n = len(W.nodes) - len(disconnected_ixs) - len(sink_ixs)

    # Dummy df_mask - renormalized later so the exact choice of damping
    # factor is not important
    df_mask = W.get_df_mask(0.99, alpha_out_map, 1.0, None)

    def _root_func(x0):
        df_mask1 = x0 * df_mask / df_mask.max()
        SPL = BasicLaplacian(W.copy(), df_mask1,
                             boundary_cols=sink_ixs)
        v = np.ones(SPL.L.shape[0], dtype='d')
        v[sink_ixs] = 0.0
        G_col_sum = SPL.solve(v, False)
        F_col_sum = np.dot(G_col_sum, SPL.boundary_col_data)
        Gsq_col_sum = SPL.solve(G_col_sum, False)
        GF_col_sum = np.dot(Gsq_col_sum, SPL.boundary_col_data)

        fval = F_col_sum.sum() / n - target_absorption_prob
        fpval = GF_col_sum.sum() / n / x0
        return fval, fpval, SPL

    x, _, _, SPL =  rootfind_newton(_root_func, 0.85, 0.0, 1.0, maxiter, tol)
    F = evaluate_context(SPL, sink_ixs)
    return x, n, F



class AbsorbingAnalysis(BasicITM):

    short_desc = 'Absorbing model'
    base_default_script = 'absorbing_base_default'
    summary_default_script = 'absorbing_summary_default'
    nodes_default_script = 'absorbing_nodes_default'
    layout_default_script = 'absorbing_layout_default'
    mode = 'absorbing'

    def __init__(self, G, sink_nodes, df=1.0, antisink_map=None, ap=None,
                 context_laplacian=None, **kwargs):

        if df is None and ap is None:
            raise RuntimeError('Invalid specification of dissipation.')

        if antisink_map is None:
            antisink_map = dict()

        excluded_nodes = [node for node in antisink_map
                          if G.has_node(node) and antisink_map[node] == 0.0]
        super(AbsorbingAnalysis, self).__init__(G, excluded_nodes, [],
                                                sink_nodes, **kwargs)

        self.df = df
        self.ap = ap

        self._solve_boundary_problem(G, antisink_map, context_laplacian)

    def _solve_boundary_problem(self, G, antisink_map, SPL=None):

        sink_ixs = [G.node2index[node] for node in self.sink_nodes]

        if SPL is not None:
            # Use the laplacian provided - no need to recreate it.
            self.F = _process_context_SPL(sink_ixs, SPL)

        else:
            W = G.weighted_adjacency_matrix()
            alpha_out_map = dict( (G.node2index[p], antisink_map[p]) \
                                  for p in antisink_map if G.has_node(p) )

            if self.df is None:
                self.df, self.connected_nodes, self.F = \
                    _process_context_mu_newton(W,
                                               sink_ixs,
                                               alpha_out_map,
                                               self.ap)
            else:
                self.F = _process_context_df(W,
                                             sink_ixs,
                                             alpha_out_map,
                                             self.df)

    def report_contexts(self):
        return [ 'Absorbing boundary: [%s] (Dissipation=%.2g)' % \
                  (', '.join(map(str,self.sink_nodes)),1.0-self.df) ]

    def _save_mode(self, conn):

        cur = conn.cursor()

        sql_insert_damping = self.db_insert_stmt('damping', 3)
        cur.execute(sql_insert_damping, (None, self.df, 1.0))
        _items = ((self.node2index[node], 0.0, 1.0) \
                  for node in self.excluded_nodes)
        cur.executemany(sql_insert_damping, _items)

        _items = ((i, self.node2index[node], 1.0) \
                  for i, node in enumerate(self.sink_nodes))
        cur.executemany(self.db_insert_stmt('sinks', 3), _items)

        _items = ((i, k, self.F[i,k]) for i in xrange(self.F.shape[0]) \
                                      for k in xrange(self.F.shape[1]))
        cur.executemany(self.db_insert_stmt('F', 3), _items)

        cur.close()




