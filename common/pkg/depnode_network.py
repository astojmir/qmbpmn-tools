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
# Code author:  Alexander Bliskovsky
#

from gluelib import DepNode
import os
from ..db_parsers.biogrid_main3 import create_network

class DepITMProbeNetwork(DepNode):
    """Create required ITM Probe networks."""

    @staticmethod
    def _term_db_files(species, directory):
        files = os.listdir(directory)
        etd_files = []
        for filename in files:
            parts = filename.split('.')
            if parts[-1] == 'etd' and parts[0] == species:
                etd_files.append(os.path.join(directory, filename))
        return etd_files

    def resolve(self):
        graph_name = self.graph_params[0]['graph_file']
        self.printmsg('Creating graph %s.' % graph_name, 2)
        etd_files = self._term_db_files(self.org_name,
                                        self.termdb_dir)
        self.graph_params[0]['enrich_files'] = etd_files
        self.kwargs['enrich_files'] = etd_files

        net_files = create_network('', **self.graph_params[0])
        self.to_be_copied.update(net_files)
        self.printmsg('Graphs created.', 4)
        self.state = 'RESOLVED'

    def remove(self):
        graph_name = self.graph_params[0]['graph_file']
        self.printmsg('Removing network %s.' % graph_name, 3)
        try:
            os.remove(self.graph_params[0]['network_file'])
            os.remove(self.graph_params[0]['graph_file'])
        except OSError:
            pass
        self.state = 'UNRESOLVED'

    def upgrade(self):
        self.printmsg('Updating graphs...', 4)
        self.printmsg('Removing old files...', 4)
        self.remove()
        self.resolve()

    def verify(self):
        configd = set(self.parent_graph.database \
          [self.name]['arguments']['graph_params'][0]['enrich_files'])
        current = set(self._term_db_files(self.org_name, self.termdb_dir))
        if configd != current:
            self.printmsg('"{0}" needs reconfiguration.'.format(self.name), 2)
            self.upgrade()
            self.printmsg('Reconfiguration complete', 4)
            return 'reconfigured'
        return 'unchanged'
