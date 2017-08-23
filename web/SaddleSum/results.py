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


def get_saddlesum_results(opts, raw_weights, termdb_file, output_format,
                          cmd_path=None):
    """
    Run saddlesum and return its output in requested format.
    """
    opts = ['-F',  output_format] + opts
    if cmd_path is None:
        cmd_path = ''
    command = os.path.join(cmd_path, 'saddlesum')
    full_args = [command] + opts + ['-', termdb_file]
    proc = Popen(full_args, bufsize=0, stdin=PIPE, stdout=PIPE, stderr=PIPE,
                 close_fds=True)
    proc.stdin.write(raw_weights)
    proc.stdin.close()
    output = proc.stdout.read()
    err_msg = proc.stderr.read().strip()
    proc.stdout.close()
    proc.stderr.close()
    proc.wait()

    if proc.returncode != 0:
        raise exc.SaddleSumError(err_msg)
    return output, full_args


def _tab_sections(output):
    lines = output.split('\n')
    data = []
    title = None
    i = 0
    for s in lines[:-1]:
        if i == 1:
            title = s[2:]
        elif i > 2:
            if s[0] == '#':
                i = 1
                yield title, data
                data = []
                title = None
                i = 0
            elif s[:3] != '---':
                data.append(s.split('\t'))
        i += 1
    yield title, data


def parse_saddlesum_tab_output(output):
    """
    Retrieve sections from saddlesum's output in TAB format.
    """
    sections = _tab_sections(output)
    summary_body = sections.next()[1]
    warning_msgs = sections.next()[1]
    unknown_ids_txt = sections.next()[1]
    relationships = sections.next()[1]
    node_props = sections.next()[1]
    namespaces = []
    for sct in sections:
        namespaces.append(sct)
    return (summary_body, warning_msgs, unknown_ids_txt, namespaces,
            relationships, node_props)


def parse_saddlesum_tab_term_scores(output):
    """
    Retrieve sections from saddlesum's output in TAB format.
    """
    sections = _tab_sections(output)
    summary_body = sections.next()[1]
    entities = sections.next()[1]
    return (summary_body, entities)


def save_query_data(raw_weights, full_args, weights_file, command_file):
    """
    Save weights and the command used to run saddlesum.
    """
    with open(weights_file, 'wb') as fp:
        fp.write(raw_weights)
    full_args[-2] = weights_file
    with open(command_file, 'wb') as fp:
        fp.write(' '.join(full_args))


def get_saddlesum_term_scores(term_id, command_file, cmd_path=None,
                              output_format='tab'):
    """
    Run saddlesum with -T option and return its output in requested format.
    """
    with open(command_file) as fp:
        full_args = fp.readline().strip().split(' ')

    full_args = full_args[0:1] + ['-T', term_id] + full_args[1:]
    if output_format == 'txt':
        full_args = full_args[:-2] + ['-F', 'txt'] + full_args[-2:]

    if cmd_path is None:
        cmd_path = ''
    command = os.path.join(cmd_path, 'saddlesum')
    proc = Popen(full_args, bufsize=0, stdin=None, stdout=PIPE, stderr=PIPE,
                 close_fds=True)
    output = proc.stdout.read()
    err_msg = proc.stderr.read().strip()
    proc.stdout.close()
    proc.stderr.close()
    proc.wait()

    if proc.returncode != 0:
        raise exc.SaddleSumError(err_msg)
    return output
