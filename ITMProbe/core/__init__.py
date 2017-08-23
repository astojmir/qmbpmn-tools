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


import os
import sqlite3
from ... import version
from ...common.utils.filesys import check_file_exists

db_schema = \
"""
CREATE TABLE shown_params(
  rnk           INTEGER PRIMARY KEY,
  property      TEXT,
  value         TEXT
);

CREATE TABLE properties(
  property      TEXT,
  value         TEXT
);

CREATE TABLE nodes(
  nodeid        INTEGER PRIMARY KEY,
  name          TEXT
);

CREATE TABLE sources(
  sourceid      INTEGER PRIMARY KEY,
  nodeid        INTEGER,
  coeff         REAL,
  FOREIGN KEY(nodeid) REFERENCES nodes(nodeid)
);

CREATE TABLE sinks(
  sinkid        INTEGER PRIMARY KEY,
  nodeid        INTEGER,
  coeff         REAL,
  FOREIGN KEY(nodeid) REFERENCES nodes(nodeid)
);

CREATE TABLE damping(
  nodeid        INTEGER,
  dfout         REAL,
  dfin          REAL,
  FOREIGN KEY(nodeid) REFERENCES nodes(nodeid)
);

CREATE TABLE F(
  nodeid        INTEGER,
  sinkid        INTEGER,
  val           REAL,
  FOREIGN KEY(sinkid) REFERENCES sinks(sinkid),
  FOREIGN KEY(nodeid) REFERENCES nodes(nodeid)
);

CREATE TABLE H(
  sourceid      INTEGER,
  nodeid        INTEGER,
  val           REAL,
  FOREIGN KEY(sourceid) REFERENCES sources(sourceid),
  FOREIGN KEY(nodeid) REFERENCES nodes(nodeid)
);
"""

class BasicITM(object):
    """
    Base for all models.
    """

    mode = None
    sql_placeholder = '?'
    params_default_script = 'input_summary_default'
    base_default_script = None
    summary_default_script = None
    nodes_default_script = None
    layout_default_script = None

    def __init__(self, G, excluded_nodes, source_nodes, sink_nodes,
                 extra_input_params=None):

        self.source_nodes = source_nodes
        self.sink_nodes = sink_nodes
        self.node2index = G.node2index
        self.G = G
        self.excluded_nodes = excluded_nodes

        if extra_input_params is not None:
            self.extra_input_params = extra_input_params
        else:
            self.extra_input_params = []

        if hasattr(G, 'name'):
            self.graph_name = self.G.name
        else:
            self.graph_name = self.G.filename

    def db_insert_stmt(self, table, num_vals):
        stmt = 'INSERT INTO %s  VALUES (%s)' % \
               (table, ', '.join([self.sql_placeholder]*num_vals))
        return stmt

    def save(self, sqlite_db):
        """
        Save all parameters and results into SQLite database.

        The parameter sqlite_db can either be a filename or an existing SQLite
        connection. In the former case, if sqlite_db exists, it is removed
        before being reinitialized. In the latter case, the connection is not
        closed after writing.
        """

        if isinstance(sqlite_db, basestring):
            if check_file_exists(sqlite_db):
                os.remove(sqlite_db)
            conn = sqlite3.connect(sqlite_db)
            close_conn = True
        else:
            conn = sqlite_db
            close_conn = False

        self._save_basic(conn)
        self._save_mode(conn)
        conn.commit()
        if close_conn:
            conn.close()

    def _save_basic(self, conn):

        cur = conn.cursor()
        cur.executescript(db_schema)

        sql_insert_params = self.db_insert_stmt('properties', 2)
        cur.execute(sql_insert_params, ('mode', self.mode))
        cur.execute(sql_insert_params, ('graph_filename', self.G.filename))
        cur.execute(sql_insert_params, ('base_default_script',
                                        self.base_default_script))
        cur.execute(sql_insert_params, ('params_default_script',
                                        self.params_default_script))
        cur.execute(sql_insert_params, ('summary_default_script',
                                        self.summary_default_script))
        cur.execute(sql_insert_params, ('nodes_default_script',
                                        self.nodes_default_script))
        cur.execute(sql_insert_params, ('layout_default_script',
                                        self.layout_default_script))

        _items = [(i, k, v) for i, (k ,v) in enumerate(self._input_params())]
        cur.executemany(self.db_insert_stmt('shown_params', 3), _items)

        _items = ((i, str(node)) for i, node in enumerate(self.G.nodes))
        cur.executemany(self.db_insert_stmt('nodes', 2), _items)

        cur.close()

    def _save_mode(self, conn):

        # To be defined by derived modes
        raise NotImplementedError

    def report_contexts(self):
        """Print context information."""
        raise NotImplementedError

    def _input_params(self):

        graph_data = '%s (%d nodes, %d links)' %\
                     (self.graph_name, self.G._num_nodes, self.G._num_edges)

        data = [['Program',
                 'ITMProbe (qmbpmn-tools-%s)' % version.CURRENT_VERSION]] + \
               self.extra_input_params + \
               [['ITM Probe model', self.short_desc]] + \
               [['Graph', graph_data]] + \
               [line.split(':') for line in self.report_contexts()] + \
               [['Excluded nodes', len(self.excluded_nodes)]]
        return data
