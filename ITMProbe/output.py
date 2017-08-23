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

import sys
import csv

def is_numeric(x):
    try:
        float(x)
        return True
    except ValueError:
        return False

def formatted_table(data, column_headers, column_formats, title):
    """ Apply text formats to table data obtained through SQL query."""

    title = title[0][0]

    if column_headers[0][0] is not None:
        column_headers = [row[0] for row in column_headers]
    else:
        column_headers = None

    if column_formats[0][0] is not None:
        column_formats = [row[0] for row in column_formats]
        body = [[fmt.format(x)for fmt, x in zip(column_formats, row)] \
                for row in data]
    else:
        column_formats = None
        body = [[str(x) for x in row] for row in data]

    numeric_cols = [False] * len(body[0])
    for row in body:
        for i, x in enumerate(row):
            numeric_cols[i] = numeric_cols[i] or is_numeric(x)

    float_cols = [i for i, x in enumerate(numeric_cols) if x]

    return title, column_headers, body, float_cols


def print_table_text(title, column_headers, body, fp=sys.stdout,
                      max_header_width=12):
    """Print table as plain text."""

    # Column widths are either the header widths or maximum lenghts of content
    if column_headers is None:
        column_widths = [0] * len(body[0])
    elif max_header_width is not None:
        column_widths = [min(len(h), max_header_width) for h in column_headers]
    else:
        column_widths = [len(h) for h in column_headers]

    for row in body:
        for i, x in enumerate(row):
            column_widths[i] = max(column_widths[i], len(x))

    # Re-format the body using new column widths
    body = [['{0:{1}.{2}}'.format(s, n, n) for s, n in zip(row, column_widths)]
                                           for row in body]

    if title is not None:
        fp.write('* %s *\n\n' % title)

    if column_headers is not None:
        column_headers = ['{0:{1}.{2}}'.format(s, n, n) \
                          for s, n in zip(column_headers, column_widths)]
        total_width = sum(column_widths) + len(column_widths) - 1
        fp.write(' '.join(column_headers))
        fp.write('\n')
        fp.write('-' * total_width)
        fp.write('\n')

    for row in body:
        fp.write(' '.join(row))
        fp.write('\n')
    fp.write('\n')


def print_table_csv(title, column_headers, body, fp=sys.stdout):
    """Print table in CSV format."""

    writer = csv.writer(fp)
    if title is not None:
        writer.writerow(['* %s *' % title])
        writer.writerow([])
    if column_headers is not None:
        writer.writerow(column_headers)
    for row in body:
        writer.writerow(row)
    writer.writerow([])


def print_table_tab(title, column_headers, body, fp=sys.stdout):
    """Print table in TAB-delimited format."""

    if title is not None:
        fp.write("#\n# %s\n#\n" % title.upper())

    if column_headers is not None:
        fp.write('\t'.join(column_headers))
        fp.write('\n')

    for row in body:
        fp.write('\t'.join(row))
        fp.write('\n')


print_table_funcs = {'txt': print_table_text,
                     'csv': print_table_csv,
                     'tab': print_table_tab,
                     }

