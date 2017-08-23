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
from subprocess import Popen, PIPE
from .. import exceptions as exc


def get_etd_info(term_db, cmd_path=None):
    """
    Parse output of saddlesum-show-etd in TAB format.
    """
    info_lines = [('db_name', str),
                  ('db_file', str),
                  ('gene_info_file', str),
                  ('tax_id', int),
                  ('num_entities', int),
                  ('num_terms', int),
                  ('num_namespaces', int)]
    etd_info = {'namespaces': []}

    if cmd_path is None:
        cmd_path = ''
    command = os.path.join(cmd_path, 'saddlesum-show-etd')
    proc = Popen([command, '-F', 'tab', term_db], bufsize=0,
                 stdin=None, stdout=PIPE, stderr=PIPE, close_fds=True)
    lines = proc.stdout.readlines()
    err_msg = proc.stderr.read().strip()
    proc.stdout.close()
    proc.stderr.close()
    proc.wait()

    if proc.returncode != 0:
        raise exc.SaddleSumError(err_msg)

    # general info
    for i, (key, data_type) in enumerate(info_lines):
        data = lines[3+i].strip().split('\t')[1]
        etd_info[key] = data_type(data)

    # namespaces
    for i in xrange(13, 13 + etd_info['num_namespaces']):
        data = lines[i].strip().split('\t')
        etd_info['namespaces'].append((data[0], int(data[1])))

    return etd_info
