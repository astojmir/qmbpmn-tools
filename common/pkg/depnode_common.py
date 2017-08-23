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

"""Code for handling all 'common' dependencies."""

from gluelib import DepNode
import urllib
import os
import sys
import shutil
import gzip

class DepURLFile(DepNode):
    """This node handles any file that must be downloaded."""

    def __init__(self, optional, parent_graph, name, verbose,  **kwargs):
        DepNode.__init__(self, optional, parent_graph, name, verbose,  **kwargs)

        self.compression = self.kwargs.get('compression', '')

        if os.path.exists(self.path):
            self.state = 'RESOLVED'

    def resolve(self):
        if self.state == 'RESOLVED':
            return

        self.printmsg('Downloading {0}...'.format(self.file_name), 2)

        res = self.get_file(self.url_fmt.format(*self.url_params),
                            self.file_name,
                            self.path + self.compression,
                            self.get_from)

        if res == 'failed':
            if self.optional:
                self.state = 'FAILED'
            else:
                sys.exit(2)
        elif res == 'copied':
            self.state = 'RESOLVED'
            return

        if self.compression == '.gz':

            self.printmsg('File is compressed. Extracting...', 3)
            gzip_fp = gzip.open(self.path + '.gz', 'rb')
            file_fp = open(self.path, 'wb')

            gzip_content = gzip_fp.read()
            file_fp.write(gzip_content)

            file_fp.close()
            gzip_fp.close()
            os.remove(self.path + '.gz')

            self.state = 'RESOLVED'
        else:
            self.state = 'RESOLVED'

        self.to_be_copied.add(os.path.normpath(self.path))

    def remove(self):
        self.printmsg('Removing file "{0}"...'.format(self.path), 2)

        try:
            os.remove(self.path)
        except OSError:
            pass

        self.state = 'UNRESOLVED'

    def upgrade(self):
        self.printmsg('Removing old file.', 3)
        self.remove()
        self.printmsg('File removed.', 4)
        self.resolve()
        self.printmsg('Updated file downloaded.', 4)

    def get_file(self, url, file_name, path, get_from):
        """Retrieve a file from the specified location."""

        if get_from is not None:
            path_to_file = os.path.join(get_from, file_name)
            if os.path.exists(path_to_file):
                shutil.copy(path_to_file, path)
                return 'copied'
        try:
            urllib.urlretrieve(url, path)
        except IOError as strerror:
            self.printmsg('Retrieval of {0} failed![{1}]'.format(file_name,
                                                                 strerror),
                          1)
            return 'failed'

        return 'downloaded'
