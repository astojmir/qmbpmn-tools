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
from ...common.graph.dmatrix import dijkstra
from ...common.utils.newton import rootfind_newton


def evaluate_context(SPL, source_ixs, sink_ixs):

    F = np.zeros((SPL.L.shape[0], len(sink_ixs)), 'd')
    H = np.zeros((SPL.L.shape[0], len(source_ixs)), 'd')

    P_S = np.zeros((len(source_ixs), SPL.L.shape[0]), 'd')
    for i, s in enumerate(source_ixs):
        P_S[i, :] = SPL.get_boundary_row(s)

    for i, k in enumerate(sink_ixs):
        F[:, i] = SPL.solve(SPL.get_boundary_col(k), True)
        F[source_ixs, i] = 0.0
        F[sink_ixs, i] = 0.0

    G_SK = np.dot(P_S, F) + P_S[:, sink_ixs]

    for i, k in enumerate(sink_ixs):
        F[k, i] = 1.0
        for j, s in enumerate(source_ixs):
            F[s, i] = G_SK[j, i]

    for j, s in enumerate(source_ixs):
        H[:, j] = SPL.solve(SPL.get_boundary_row(s), False)
        H[source_ixs, j] = 0.0
        H[sink_ixs, j] = 0.0
        for i, k in enumerate(sink_ixs):
            H[k, j] = G_SK[j, i]

        # This line must be last to take into account sources that are also
        # sinks. This way everything is consistent.
        H[s, j] = 1.0

    return F, H


def _context_arg_check(W, df_mask, source_ixs, sink_ixs):
    """
    Checks that there is a path from each source to one of the sinks.

    Sets df_mask so that only the union of connected components is revealed
    (this insures the solution will exist for df=1.0).
    Also returns the average of minimum path lengths source to sink.
    """

    A = W.copy().adjacency_matrix

    # Incoming links to all sources and outgoing links to all sinks must be
    # zeroed
    tmp = np.ones(A.shape[0], 'd')
    tmp[source_ixs] = 0.0
    col_mask = tmp[A.indices]
    np.multiply(col_mask, A.data, A.data)

    for k in sink_ixs:
        A.data[A.indptr[k]:A.indptr[k+1]] = 0.0

    # Lower bound is the length of the shortest path to any sink: we use
    # dijkstra. We need to first copy the adjacency pattern and zero out the
    # links that are removed by df mask. Dijkstra returns the full connected
    # component of the source (outward)
    A.data[df_mask == 0] = np.inf
    A.data[df_mask != 0] = 1.0

    src_valid_nodes = set()
    avg_shortest_pathlen = 0
    for src in source_ixs:
        D, _ = dijkstra(A, src)
        src_valid_nodes.update(D.iterkeys())
        avg_shortest_pathlen += min(D.get(k, np.inf) for k in sink_ixs)

    if np.isinf(avg_shortest_pathlen):
        raise RuntimeError('At least one source must be connected to any'
                           ' of the sinks.')
    avg_shortest_pathlen /= len(source_ixs)

    # Find indices that are not in the connected component source -> sinks
    # and zero out their links in df_mask. We already have the nodes
    # reachable from the source but we also need nodes that can reach sinks.
    snk_valid_nodes = set()

    A = A.T.tocsr()
    A.sort_indices()
    for snk in sink_ixs:
        snk_valid_nodes |= set(dijkstra(A, snk)[0].iterkeys())

    valid_nodes = src_valid_nodes & snk_valid_nodes
    disconnected = list(set(range(A.shape[0])) - valid_nodes)

    # Zero the rows of disconnected component
    for j in disconnected:
        row_start = A.indptr[j]
        row_end = A.indptr[j+1]
        df_mask[row_start:row_end] = 0.0

    # Now zero the columns
    tmp[:] = 1.0
    tmp[disconnected] = 0.0
    col_mask = tmp[A.indices]
    np.multiply(col_mask, df_mask, df_mask)

    return df_mask, avg_shortest_pathlen


def _process_context_SPL(source_ixs, sink_ixs, SPL):

    SPL.set_boundary_ixs(sink_ixs + source_ixs)
    return evaluate_context(SPL, source_ixs, sink_ixs)


def _process_context_df(W,
                        source_ixs,
                        sink_ixs,
                        alpha_out_map,
                        df):

    if df < 1e-14:
        raise RuntimeError('Cannot evaluate a context with a damping factor'
                           ' too close to 0.')

    df_mask = W.get_df_mask(df, alpha_out_map, 1.0, None)
    if df > (1 - 1e-14):
        df_mask, _ = _context_arg_check(W, df_mask, source_ixs, sink_ixs)
        df_mask *= df

    SPL = BasicLaplacian(W, df_mask,
                         boundary_rows=source_ixs + sink_ixs,
                         boundary_cols=sink_ixs + source_ixs)
    return evaluate_context(SPL, source_ixs, sink_ixs)


def _process_context_mu_newton(W,
                               source_ixs,
                               sink_ixs,
                               alpha_out_map,
                               avg_path_length_deviation,
                               relative=False,
                               maxiter=50,
                               tol=1.0e-11):

    df_mask = W.get_df_mask(0.85, alpha_out_map, 1.0, None)

    # Get lower bound - shortest path from any of active source to any sink
    df_mask, lower = _context_arg_check(W, df_mask, source_ixs, sink_ixs)

    # Relative path_length deviation - in terms of the shortest path length
    if relative:
        avg_path_length_deviation *= lower
    target_avg_path_length = lower + avg_path_length_deviation
    if (target_avg_path_length < lower):
        raise RuntimeError('Given target path length is outside bounds.')

    def _root_func(x0):
        df_mask1 = x0 * df_mask / df_mask.max()
        SPL = BasicLaplacian(W.copy(), df_mask1,
                             boundary_rows=source_ixs+sink_ixs,
                             boundary_cols=sink_ixs+source_ixs)

        Fs = np.zeros(len(sink_ixs), 'd')
        Ts = np.zeros(len(sink_ixs), 'd')
        DTs = np.zeros(len(sink_ixs), 'd')
        fval = 0.0
        fpval = 0.0

        for s in source_ixs:
            Fs[:] = 0.0
            Ts[:] = 0.0
            DTs[:] = 0.0
            P_row_s = SPL.get_boundary_row(s)
            # Calculate F_{sK} and F_{sk}
            for j, k in enumerate(sink_ixs):
                F_col_k = SPL.solve(SPL.get_boundary_col(k), True)
                GF_col_k = SPL.solve(F_col_k, True)
                GGF_col_k = SPL.solve(GF_col_k, True)
                Fs[j] = np.dot(P_row_s, F_col_k)
                HF_sk = np.dot(P_row_s, GF_col_k)
                HGF_sk = np.dot(P_row_s, GGF_col_k)
                Ts[j] = (1.0 + HF_sk / Fs[j])
                DTs[j] = (Ts[j] - Ts[j]**2 + 2.0 * HGF_sk / Fs[j]) / x0

            fval += (Fs * Ts / Fs.sum()).sum()
            fpval += (Fs * DTs / Fs.sum()).sum()

        fval /= len(source_ixs)
        fval -= target_avg_path_length
        fpval /= len(source_ixs)
        return fval, fpval, SPL

    a = 0.0   # lower bound for df
    b = 1.0   # upper bound for df - see comment below
    x0 = 0.8  # starting guess
    x, _, _, SPL = rootfind_newton(_root_func, x0, a, b, maxiter, tol)
    F, H = evaluate_context(SPL, source_ixs, sink_ixs)
    return x, F, H


class NormChannelAnalysis(BasicITM):

    short_desc = 'Normalized channel model'
    base_default_script = 'nchannel_base_default'
    summary_default_script = 'nchannel_summary_default'
    nodes_default_script = 'nchannel_nodes_default'
    layout_default_script = 'nchannel_layout_default'
    mode = 'nchannel'

    def __init__(self, G, source_nodes, sink_nodes, df=1.0, da=None, dr=None,
                 antisink_map=None, context_laplacian=None, **kwargs):

        if df is None and da is None and dr is None:
            raise RuntimeError('Invalid specification of dissipation.')

        if antisink_map is None:
            antisink_map = dict()

        excluded_nodes = [node for node in antisink_map
                          if G.has_node(node) and antisink_map[node] == 0.0]
        super(NormChannelAnalysis, self).__init__(G, excluded_nodes,
                                                  source_nodes, sink_nodes,
                                                  **kwargs)

        self.df = df
        self.da = da
        self.dr = dr

        self._solve_boundary_problem(G, antisink_map, context_laplacian)

    def _solve_boundary_problem(self, G, antisink_map, SPL=None):

        source_ixs = [G.node2index[node] for node in self.source_nodes]
        sink_ixs = [G.node2index[node] for node in self.sink_nodes]

        if SPL is not None:
            # Use the laplacian provided - no need to recreate it.
            F, H = _process_context_SPL(source_ixs, sink_ixs, SPL)

        else:
            W = G.weighted_adjacency_matrix()
            alpha_out_map = dict( (G.node2index[p], antisink_map[p])
                                  for p in antisink_map if G.has_node(p) )

            if self.df is not None:
                # Standard processing
                F, H = _process_context_df(W,
                                           source_ixs,
                                           sink_ixs,
                                           alpha_out_map,
                                           self.df)
            elif self.da is not None:
                # Deviation from shortest path (averaged) - absolute
                self.df, F, H = _process_context_mu_newton(W,
                                                           source_ixs,
                                                           sink_ixs,
                                                           alpha_out_map,
                                                           self.da)
            elif self.dr is not None:
                # Deviation from shortest path (averaged) - absolute
                self.df, F, H = _process_context_mu_newton(W,
                                                           source_ixs,
                                                           sink_ixs,
                                                           alpha_out_map,
                                                           self.dr,
                                                           True)

        self.F = F
        self.H = H

    def report_contexts(self):
        return ['Context: [%s]  -> [%s] (Dissipation=%.2g)' % \
                 (', '.join(map(str,self.source_nodes)),
                  ', '.join(map(str,self.sink_nodes)),
                  1.0-self.df)]

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

        _items = ((i, self.node2index[node], 1.0) \
                  for i, node in enumerate(self.sink_nodes))
        cur.executemany(self.db_insert_stmt('sinks', 3), _items)

        _items = ((i, k, self.F[i, k]) for i in xrange(self.F.shape[0]) \
                                       for k in xrange(self.F.shape[1]))
        cur.executemany(self.db_insert_stmt('F', 3), _items)

        _items = ((s, i, self.H[i, s]) for i in xrange(self.H.shape[0]) \
                                       for s in xrange(self.H.shape[1]))
        cur.executemany(self.db_insert_stmt('H', 3), _items)

        # Create an index on H which ought to speed up the script
        cur.execute('CREATE INDEX Hnodeindx ON H (nodeid)')
        cur.close()
