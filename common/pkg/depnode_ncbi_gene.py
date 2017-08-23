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

import sys
import os
from gluelib import DepNode
from ..db_parsers import ncbi_gene


class DepNCBIIndex(DepNode):
    """Index NCBI Gene Info files."""

    def resolve(self):
        self.printmsg('Indexing NCBI Gene %s.' % self.gene_info_index, 3)
        with open(self.gene_info_index, 'wb') as fp_out:
            ncbi_gene.index_gene_info(fp_out,
                                      self.gene_info_file,
                                      self.tax_id)
        self.to_be_copied.add(self.gene_info_index)
        self.state = 'RESOLVED'

    def remove(self):
        self.printmsg('Removing NCBI Gene index %s.' % self.gene_info_index, 3)

        try:
            os.remove(self.gene_info_index)
        except OSError:
            pass

        self.state = 'UNRESOLVED'

    def upgrade(self):
        self.remove()
        self.resolve()

