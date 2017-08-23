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
# Code author:  Alexander Bliskovsky and Aleksandar Stojmirovic
#

"""Code for handling specific needs of the Gene Ontology db."""

from gluelib import DepNode
import os
from ..utils.filesys import makedirs2
from ..db_parsers import etermdb


class DepCombinedETD(DepNode):
    """Create GO + KEGG extended term database"""

    def resolve(self):
        db_name = self.kwopts['output_file']
        self.printmsg('Creating combined term database %s.' % db_name, 3)
        self._add_storage_dir(self.storage_dir, self.kwopts, ['output_file'])
        etermdb.create_combined_etd(**self.kwopts)
        self.to_be_copied.update([self.kwopts['output_file']])
        self.state = 'RESOLVED'

    def remove(self):
        db_name = self.kwopts['output_file']
        self.printmsg('Removing ETD file %s.' % db_name, 4)
        self._add_storage_dir(self.storage_dir, self.kwopts, ['output_file'])
        try:
            os.remove(self.kwopts['output_file'])
        except OSError:
            pass


class DepGO2Gmt(DepNode):
    """Create GMT database from a GO namespace"""

    def resolve(self):
        db_name = self.kwopts['output_file']
        self.printmsg('Creating GMT term database %s.' % db_name, 3)
        self._add_storage_dir(self.storage_dir, self.kwopts, ['output_file'])
        etermdb.create_go_gmt(**self.kwopts)
        self.to_be_copied.update([self.kwopts['output_file']])
        self.state = 'RESOLVED'

    def remove(self):
        db_name = self.kwopts['output_file']
        self.printmsg('Removing GMT file %s.' % db_name, 4)
        self._add_storage_dir(self.storage_dir, self.kwopts, ['output_file'])
        try:
            os.remove(self.kwopts['output_file'])
        except OSError:
            pass

    def upgrade(self):
        self.remove()
        self.resolve()


class DepKEGG2Gmt(DepNode):
    """Create GMT database from KEGG pathways"""

    def resolve(self):
        db_name = self.kwopts['output_file']
        self.printmsg('Creating GMT term database %s.' % db_name, 3)
        self._add_storage_dir(self.storage_dir, self.kwopts, ['output_file'])
        etermdb.create_kegg_gmt(**self.kwopts)
        self.to_be_copied.update([self.kwopts['output_file']])
        self.state = 'RESOLVED'

    def remove(self):
        db_name = self.kwopts['output_file']
        self.printmsg('Removing GMT file %s.' % db_name, 4)
        self._add_storage_dir(self.storage_dir, self.kwopts, ['output_file'])
        try:
            os.remove(self.kwopts['output_file'])
        except OSError:
            pass

    def upgrade(self):
        self.remove()
        self.resolve()
