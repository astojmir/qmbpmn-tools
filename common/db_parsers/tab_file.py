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



class TabFileParser(object):

    def __init__(self):
        self.skip_initial_lines = 0
        self._header_counter = 0
        self.header_callback = self._header_callback_default
        self.filter_callback = self._filter_callback_default

    def _header_callback_default(self, line):
        self._header_counter += 1
        if self._header_counter >= self.skip_initial_lines:
            return True
        return False

    def _filter_callback_default(self, fields):
        return None

    def _reset(self):
        self.header_counter = 0

    def parse_file(self, filename, graph_class):

        self._reset()
        G = graph_class()
        with open(filename, 'r'):

            # Skip header lines until header_callback returns True
            if self.skip_initial_lines:
                for line in fp:
                    if self.header_callback(line):
                        break

            # Scan each proper line using filter_callback
            for line in fp:
                fields = line.strip().split('\t')
                interaction = self.filter_callback(fields)
                if interaction != None:
                    p1, p2 = interaction
                    G.insert_edge(p1, p2)

        return G

class SimpleParser(TabFileParser):
    """
    Simplest parser: two columns, tab separted.
    """
    def _filter_callback_default(self, fields):
        return fields[0], fields[1]
