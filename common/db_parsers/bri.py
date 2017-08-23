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
# Code authors:  Alexander Bliskovsky and Aleksandar Stojmirovic
#

"""
Code for dealing with KEGG pathway databases as controlled vocabularies.
"""
import re
from .cvterm import CVTerm


class KEGGTerm(CVTerm):
    """
    KEGG Term Object

    :param `term_id`: The numerical ID of the term.
    :param `namespace`: Namespace of the term. This is derived
                        from the brite file used.
    :param `name`: The full name of the term.
    :param `url_fmt`: A list of 2 URLs. The first being the url
                      which points to the 'path' level and the
                      second which points to the 'object' or
                      'leaf' level.

    :keyword term_type: The indentation level and index. For example
                        'A3' or 'B4'. 'C' level terms do not have
                        indices because they have a numerical term ID.
    :keyword org_prefix: The KEGG organism prefix. i.e. 'sce' or 'hsa'.

    """

    dot_graph_name = ""

    def __init__(self, term_id, namespace, name, url_fmt,
                 **kwargs):

        super(KEGGTerm, self).__init__(term_id, namespace, name, url_fmt)

        self.__dict__.update(kwargs)
        self.path_level_url_fmt = url_fmt[0]
        self.obj_level_url_fmt = url_fmt[1]

    def url(self):
        """Format a url to point to the entry in KEGG"""
        if self.term_type != 'C':
            url_fmt = self.path_level_url_fmt
            url_info = {'id': self.term_type}
        else:
            url_fmt = self.obj_level_url_fmt
            url_info = {'org_prefix': self.org_prefix, 'id': self.term_id}

        return url_fmt % url_info

    def format_id(self, html=False):
        """Format term id for output.

           The term ID for level 'A' and 'B' terms is the same
           as their name. We replace this for display with their
           indentation level and index.

           :see: KEGGTerm.term_type
        """
        if self.term_type == 'C':
            full_id = 'KEGG:' + self.org_prefix + self.term_id
        else:
            full_id = 'KEGG:' + self.term_type

        if html:
            term_id = self.id_anchor_fmt % (self.url(), full_id)
        else:
            term_id = full_id
        return term_id

    def dot_node_attrs(self):
        """Attributes for the graph node corresponding to the term to be passed
        to graphviz dot.
        """

        lbl_name = '%s' % self.format_name(True, True, 24)
        lbl_acc = '<font point-size="8.0">%s</font>' % self.format_id()
        label = self.node_label_fmt % (self.url(), self.name,
                                       lbl_name, lbl_acc)

        node_attrs = {'label': label}
        return node_attrs


class KEGGOntology(object):
    """Stores and provides relationships between terms from KEGG brite.
    """

    def __init__(self, kegg_brite, obj_level_url_fmt=None,
                 path_level_url_fmt=None, org_prefix=None):
        """
        Parse the brite file and other set up.

        :param `kegg_brite`: The KEGG brite file path.
        :param `obj_level_url_fmt`: URL format for leaf terms within the
                                    hierarchy
        :param `path_level_url_fmt`: URL format for inner terms within the
                                     hierarchy
        :param `org_prefix`: standard KEGG organism prefix
        """

        self.org_prefix = org_prefix
        self.namespace = None
        self.index2terms = []
        self.term2type = {}
        self.terms = {}
        self.term2parent = self._load_brite(kegg_brite)
        self.obj_level_url_fmt = obj_level_url_fmt
        self.path_level_url_fmt = path_level_url_fmt
        self.term2index = \
          dict((t, i) for i, t in enumerate(self.index2terms))

    def _load_brite(self, brite_file):

        with open(brite_file, 'rb') as file_fp:

            term2parent = {'KEGG Pathway': None}

            # The breadcrumb trail goes from most specific to least
            # specific. New entries are inserted at the beginning, not
            # the end. This way we don't have to fiddle with lengths.
            breadcrumb = []

            a_ct = 1
            b_ct = 1

            for line in file_fp:
                if line[0] == '#':
                    #We ignore comments.
                    continue

                elif line[0] == 'A':
                    # This is the top level of indentation. All 'A' level
                    # terms will have 'KEGG Pathway' as their parent.

                    parent_term = 'KEGG Pathway'

                    # This matches text in between the <b> tags.
                    regex_pattern = r'<b>([^<]*)</b>'
                    match = re.search(regex_pattern, line)

                    if match is not None:

                        term = match.group(1)
                        term2parent[term] = parent_term

                        # Since this is the topmost level of indentation, the
                        # breadcrumb trail can  be reset each time we hit an
                        #A level indent.

                        breadcrumb = [term]
                        self.terms[term] = term
                        self.term2type[term] = 'A' + str(a_ct)
                        a_ct += 1

                elif line[0] == 'B':

                    # If another 'B' level term is in the breadcrumb trail,
                    # get rid of it. We will replace it with this term.
                    if len(breadcrumb) > 1:
                        breadcrumb.pop(0)

                    # No regex is required because the 'B' level terms have no
                    # formatting aside from simple padding.
                    term = line[1:].strip()

                    parent_term = breadcrumb[0]
                    term2parent[term] = parent_term

                    breadcrumb.insert(0, term)

                    self.terms[term] = term
                    self.term2type[term] = 'B' + str(b_ct)
                    b_ct += 1

                elif line[0] == 'C':

                    # This extracts the 5 digit code as the first group and
                    # the description of the cell as the second group.
                    regex_pattern = r'\s+(\d{5})\s+(.*)'

                    match = re.search(regex_pattern, line[1:])
                    kegg_id = match.group(1)
                    name = match.group(2)

                    self.index2terms.append(kegg_id)

                    # The 5 digit ID is more specific than the name. Therefore
                    # the ID is the child of the name.
                    term2parent[kegg_id] = breadcrumb[0]
                    term2parent[name] = breadcrumb[0]

                    self.terms[kegg_id] = name
                    self.term2type[kegg_id] = 'C'

        return term2parent

    def transitive_closure(self, term_id_list):
        """Return the transitive closure between the start term and the root.

        This returns a tuple of two objects:

        - visited:
                   A set of nodes that are involved in the
                   transitive closure.
        - edges:
                 A set of the relationships between nodes. 'is_a' is the only
                 relationship used by KEGG.

        :param `term_id_list`: list of initial starting points (terms)
        """

        edges = set()
        visited = set(term_id_list)

        for term_id in term_id_list:
            current_term = term_id

            while current_term != 'KEGG Pathway':
                next_term = self.term2parent[current_term]
                edges.add((current_term, 'is_a', next_term))
                visited.add(current_term)
                current_term = next_term

        return visited, edges

    def get_term(self, term_id=None, term_index=None):
        """
        Return a KEGGTerm instance given either the term_id or term_index.
        """

        assert (1 == (term_id is None) + (term_index is None)), \
               "Exactly one of term_id or term_index must be specified."

        if term_id is None:
            term_id = self.index2terms[term_index]

        term_dict = {'term_id': term_id,
                     'namespace': 'KEGG Pathways',
                     'name': self.terms[term_id],
                     'term_type': self.term2type[term_id],
                     'org_prefix': self.org_prefix,
                     'url_fmt': [self.path_level_url_fmt,
                                 self.obj_level_url_fmt]
                     }

        return KEGGTerm(**term_dict)
