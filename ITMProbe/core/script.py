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

""" Routines and classes for processing ITM scripts."""

from ...common.pyparsing import Regex
from ...common.pyparsing import Literal
from ...common.pyparsing import ZeroOrMore
from ...common.pyparsing import Group
from ...common.pyparsing import OneOrMore
from ...common.pyparsing import ParseFatalException
import sqlite3

# Functions made available to scripts through SQL
def srccol(i, tbl):
    """SQL statement for pivoting in H on given source """
    return 'sum(%s.val*delta(%s.sourceid, %d)) AS datacol%d' % \
           (tbl, tbl, i, i)


def snkcol(i, tbl):
    """SQL statement for pivoting in F on given sink """
    return 'sum(%s.val*delta(%s.sinkid, %d))  AS datacol%d' % \
           (tbl, tbl, i, i)


def delta(i, j):
    """Delta function to enable pivoting """
    return 1 if i == j else 0


class ParticipationRatio(object):
    """ Participation ratio of a column """
    def __init__(self):
        self.sum = 0
        self.sq_sum = 0

    def step(self, x):
        self.sum += abs(x)
        self.sq_sum += x**2

    def finalize(self):
        return self.sum ** 2 / self.sq_sum


class MissingVarException(Exception):
    """
    Exception to raise when the script does not define all required variables
    """
    def __init__(self, var):
        self.var = var

    def __str__(self):
        return 'Required script variable %s is not defined.' % self.var


def connect_main_db(main_db):
    """
    Produces an SQLite connection with our own additional functions etc.
    """
    conn = sqlite3.connect(main_db)
    conn.text_factory = str
    conn.create_function('pow', 2, pow)
    conn.create_function('srccol', 2, srccol)
    conn.create_function('snkcol', 2, snkcol)
    conn.create_function('delta', 2, delta)
    conn.create_aggregate('participation_ratio', 1, ParticipationRatio)
    return conn


class ScriptContext(object):
    """
    Context for running ITMProbe scripts.
    """

    def __init__(self, final_vars, databases):

        self._current_val = None
        self._defined_vars = None

        self._final_vars = final_vars
        self.main_db = databases[0]
        self.attached_dbs = databases[1:]
        self.db_names = set(['main'])

        if isinstance(self.main_db, basestring):
            self.conn = connect_main_db(self.main_db)
            self.new_main_db = True
        else:
            self.conn = self.main_db
            self.new_main_db = False

        self.cur = self.conn.cursor()
        for i, db in enumerate(self.attached_dbs):
            db_name = 'db%d' % i
            self.db_names.add(db_name)
            self.cur.execute('ATTACH DATABASE ? AS ?', (db, db_name))
        self.cur.execute('PRAGMA recursive_triggers = 1')

    def __enter__( self ):

        return self

    def __exit__( self, exc_type, exc_val, exc_tb ):

        self.cur.close()
        if self.new_main_db:
            self.conn.close()
        if exc_type is not None:
            return False
        return True

    def create_function(self, name, num_args, func):
        """Add a function to SQL engine """
        self.conn.create_function(name, num_args, func)

    def get_properties(self, db_name='main'):
        """
        Retrieve the properties dictionary stored in the database.
        """
        stmt = 'SELECT property, value FROM %s.properties'
        if db_name not in self.db_names:
            raise RuntimeError('Invalid db_name specified.')
        self.cur.execute(stmt % db_name)
        res = self.cur.fetchall()
        props = dict((key, val) for key, val in res)
        return props

    def execute(self, script, defined_vars=None):
        """
        Execute a script.
        """

        self._current_val = None
        self._defined_vars = {'$semicolumn$': ';'}
        if defined_vars is not None:
            self._defined_vars.update(defined_vars)

        self._parse_script(script)

        for stmt in self.statements:
            var = stmt[0]
            for i in xrange(1, len(stmt)):
                if len(stmt[i]) and stmt[i][0] == '$':
                    # Remember that the parser ensures that this is indeed
                    # a variable to be substituted
                    stmt[i] = self._defined_vars[stmt[i]]
            full_sql_stmt = ''.join(stmt[1:])
            self.cur.execute(full_sql_stmt)
            res = self.cur.fetchall()
            if var[0] == '@':
                self._defined_vars[var] = res
            else: # var[0] == '$'
                if len(res):
                    self._defined_vars[var] = str(res[0][0])
                else:
                    self._defined_vars[var] = None

            final = {}
            for _var in self._final_vars:
                var = '@%s' % _var
                final[_var] = self._defined_vars[var]

        return final

    def _set_var(self, s, loc, toks):
        self._current_val = toks[0]

    def _add_var(self, s, loc, toks):
        self._defined_vars[self._current_val] = None
        self._current_val = None

    def _check_var(self, s, loc, toks):
        if toks[0] not in self._defined_vars:
            msg = 'Variable %s is not defined' % toks[0]
            raise ParseFatalException(s, loc,  msg)

    def _validate_statements(self):
        for _var in self._final_vars:
            var = '@%s' % _var
            if var not in self._defined_vars:
                raise MissingVarException(var)

    def _parse_script(self, script_buffer):

        stringVarLeft = Regex("\$\\w+\$")
        stringVarRight = stringVarLeft.copy()
        stringVarLeft.setParseAction(self._set_var)
        stringVarRight.setParseAction(self._check_var)
        tableVar = Regex("\@\\w+")
        tableVar.setParseAction(self._set_var)
        assignOp = Literal(":=").suppress()
        endStmt = Literal(";").suppress()
        endStmt.setParseAction(self._add_var)
        unparsedText = Regex("[^;$]*").leaveWhitespace()
        expr = ZeroOrMore(unparsedText + stringVarRight) + unparsedText
        variable = stringVarLeft | tableVar
        stmt = Group(variable + assignOp + expr + endStmt)
        script = OneOrMore(stmt)

        self.statements = script.parseString(script_buffer, True)
        self._validate_statements()
