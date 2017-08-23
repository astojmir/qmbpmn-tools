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

"""General interface for vocabulary terms."""
import textwrap

class CVTerm(object):
    """Base class for terms from controlled vocabularies.

    Provides only the interface.
    """

    text_wrapper = textwrap.TextWrapper(width=40, break_long_words=False)
    id_anchor_fmt = '<a href="%s" target="_blank">%s</a>'
    node_label_fmt = '<<table border="0" href="%s" target="_blank" title="%s">'\
                     '<tr><td>%s</td></tr><tr><td>%s</td></tr></table>>'

    def __init__(self, term_id, namespace, name, url_fmt=None):

        self.term_id = term_id
        self.namespace = namespace
        self.name = name
        self.url_fmt = url_fmt

    def url(self):
        """URL for the information about the term."""

        if self.url_fmt is not None:
            return self.url_fmt % self.term_id
        else:
            msg = 'Cannot produce URL for a term %s' % self.term_id
            raise RuntimeError(msg)

    def format_id(self, html=False):
        """Format term id for output."""

        if html:
            term_id = self.id_anchor_fmt % (self.url(), self.term_id)
        else:
            term_id = self.term_id
        return term_id


    def _wrap(self, text, width=40):
        self.text_wrapper.width = width
        return self.text_wrapper.wrap(text)

    def format_name(self, html=False, wrap=False, width=40):
        """Format term name for output."""

        if wrap:
            line_break = r'<br/>' if html else r'\n'
            formatted_name = line_break.join(self._wrap(self.name, width))
        else:
            formatted_name = self.name

        return formatted_name

    def dot_node_attrs(self):
        """Attributes for the graph node corresponding to the term to be passed
        to graphviz dot.
        """

        lbl_name = '%s' % self.format_name(True, True, 24)
        lbl_acc = '<font point-size="8.0">%s</font>' % self.term_id
        label = self.node_label_fmt % (self.url(), self.name, lbl_name, lbl_acc)

        node_attrs = {'label': label}
        return node_attrs
