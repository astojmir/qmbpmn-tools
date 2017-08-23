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


from ..graph.digraph import DirectedGraph
import re
import array
from .cvterm import CVTerm


class OBOTerm(CVTerm):
    """Open Biomedical Ontologies term."""

    dot_graph_name = "ontology_part"

    def __init__(self, term_id, namespace, name, ontology,
                 url_fmt=None, relationships=None, **kwargs):

        super(OBOTerm, self).__init__(term_id, namespace, name, url_fmt)

        self.relationships = relationships if relationships is not None else []
        self.ontology = ontology
        self.__dict__.update(kwargs)
        self._key = ontology.term2index[self.term_id]


    def __repr__(self):
        return '<OBOTerm %s>' % self.term_id


    def __str__(self):
        return  '%s(%s)' % (self.term_id, self.name)


    def __eq__(self, other):
        return self._key == other._key


    def __ne__(self, other):
        return self._key != other._key


    def __lt__(self, other):
        return self._key < other._key


    def __le__(self, other):
        return self._key <= other._key


    def __gt__(self, other):
        return self._key > other._key


    def __ge__(self, other):
        return self._key >= other._key

    def __hash__(self):
        return hash(self._key)

    def compare_to(self, other, cache=None):
        """
        Compares the term to other according to the partial order induced by
        ontology.

        Here, term A is related to (included in, finer than, <= ) term B if
        there is a directed path of 'is_a' relationships from A to B. This
        function returns 0 if self == other, 1 if self <= other, -1 if other <=
        self and None if self and other are not comparable. The argument cache
        should be either None or a dictionary storing previously computed
        values for faster retrieval.
        """

        if self == other:
            return 0
        a, b = (self, other)
        if cache is not None and (a,b) in cache:
            return cache[(a, b)]
        parents, _ = self.ontology.transitive_closure([a.term_id])
        if b.term_id in parents:
            retval = 1
        else:
            parents, _ = self.ontology.transitive_closure([b.term_id])
            if a.term_id in parents:
                retval = -1
            else:
                retval = None
        if cache is not None:
            cache[(a,b)] = retval
        return retval


class OBOntology(object):

    # Escape characters
    ESCAPED_CHARS = [(r'\n', '\n'),
                     (r'\W', ' '),
                     (r'\t', '\t'),
                     (r'\:', ':'),
                     (r'\,', ','),
                     (r'\"', '"'),
                     (r'\\', '\\'),
                     (r'\(', '('),
                     (r'\)', ')'),
                     (r'\[', '['),
                     (r'\]', ']'),
                     (r'\{', '{'),
                     (r'\}', '}'),
                     ('\n', ''),]

    SECTCRE = re.compile(r'\[(?P<header>[^]]+)\]')
    DESCRE = re.compile(r'"(?P<desc>.*)"')
    PROC_FUNCS = {'id': '_process_name',
                  'name': '_process_name',
                  'namespace': '_process_name',
                  'def': '_process_desc',
                  'is_a': '_process_is_a',
                  'relationship': '_process_relationship',
                  'is_transitive': '_process_is_transitive',
                  'transitive_over': '_process_transitive_over',
                  'is_obsolete': '_process_obsolete',
                  }

    def __init__(self, obo_filename, term_url_fmt=None):

        self.obo_filename = obo_filename
        self.term_url_fmt = term_url_fmt
        self.terms = {}
        self.index2terms = []
        self.term2index = {}
        self.typedefs = {}
        self.is_fully_parsed = False

        with open(obo_filename, 'rb') as obo_fp:
            self._parse_entire_obo_file(obo_fp)

    def get_term(self, term_id=None, term_index=None):

        assert (1 == (term_id is None) + (term_index is None)), \
               "Exactly one of term_id or term_index must be specified."

        if term_id is None:
            term_id = self.index2terms[term_index]
        term_dict = self.terms[term_id]
        return OBOTerm(ontology=self, url_fmt=self.term_url_fmt,
                       **term_dict)

    def _replace_escape_chars(self, s):

        for c, r in self.ESCAPED_CHARS:
            s = s.replace(c, r)
        return s

    def _parse_stanza_body(self, obo_fp):

        next_stanza_name = None
        tag_value_lines = []
        while True:
            line = obo_fp.readline()
            # EOF
            if line == '':
                break
            # comment or blank line?
            if line.strip() == '' or line[0] == '!':
                continue
            # next stanza name ?
            mo = self.SECTCRE.match(line)
            if mo:
                next_stanza_name = mo.group('header')
                break
            # otherwise assume a name-tag line
            # We deliberately allow things to break here if the line is no good.
            tag, raw_value = line.split(': ', 1)
            value = raw_value.split(' ! ')[0] # the rest is comment
            tag_value_lines.append((tag, value))

        return tag_value_lines, next_stanza_name


    def _process_name(self, term_dict, tag, value):
        value = self._replace_escape_chars(value)
        term_dict[tag] = value

    def _process_desc(self, term_dict, tag, value):

        mo = self.DESCRE.match(value)
        if mo:
            desc = mo.group('desc')
        else:
            desc = ''
        value = self._replace_escape_chars(desc)
        term_dict[tag] = value

    def _process_is_a(self, term_dict, tag, value):
        if 'relationships' not in term_dict:
            term_dict['relationships'] = []
        term_dict['relationships'].append(('is_a', value.strip()))

    def _process_is_transitive(self, term_dict, tag, value):
        if bool(value):
            if 'transitive_over' not in term_dict:
                term_dict['transitive_over'] = set()
            term_dict['transitive_over'].add(term_dict['id'])

    def _process_transitive_over(self, term_dict, tag, value):
        if 'transitive_over' not in term_dict:
            term_dict['transitive_over'] = set()
        term_dict['transitive_over'].add(value)

    def _process_relationship(self, term_dict, tag, value):
        if 'relationships' not in term_dict:
            term_dict['relationships'] = []
        rtype, pid = value.strip().split()[:2]
        term_dict['relationships'].append((rtype, pid))

    def _process_obsolete(self, term_dict, tag, value):
        value = value.strip()
        if value == 'true':
            term_dict['is_obsolete'] = True


    def _get_next_record(self, stanza_name, obo_fp):

        term_dict = {'record_type': stanza_name,
                     'raw_lines': []}
        tag_value_lines, next_stanza_name = self._parse_stanza_body(obo_fp)

        for tag, value in tag_value_lines:
            if tag in self.PROC_FUNCS:
                processing_method = getattr(self, self.PROC_FUNCS[tag])
                processing_method(term_dict, tag, value)
            else:
                term_dict['raw_lines'].append((tag, value))
        return term_dict, next_stanza_name


    def _parse_entire_obo_file(self, obo_fp):

        next_stanza_name = 'HEADER'
        while next_stanza_name:
            stanza_dict, next_stanza_name = \
              self._get_next_record(next_stanza_name, obo_fp)
            if stanza_dict['record_type'] == 'Term':
                term_id = stanza_dict.pop('id')
                stanza_dict['term_id'] = term_id
                self.terms[term_id] = stanza_dict
            elif stanza_dict['record_type'] == 'Typedef':
                self.typedefs[stanza_dict['id']] = stanza_dict

        self.index2terms = sorted(self.terms.iterkeys())
        self.term2index = dict((t, i) for i, t in enumerate(self.index2terms))
        # Expand the transitivity of typedefs
        self._expand_typedefs()
        self.is_fully_parsed = True

    def _expand_typedefs(self):

        # self.typedefs must be fully loaded for this
        for key in self.typedefs.keys():
            if 'transitive_over' not in self.typedefs[key]:
                self.typedefs[key]['transitive_over'] = set()
            unvisited = set()
            unvisited.add(key)
            while unvisited:
                u = unvisited.pop()
                if 'transitive_over' in self.typedefs[u]:
                    rels = self.typedefs[u]['transitive_over']
                    self.typedefs[key]['transitive_over'].update(rels)
                if 'relationships' in self.typedefs[u]:
                    for rtype, rval in self.typedefs[u]['relationships']:
                        if rtype == 'is_a':
                            unvisited.add(rval)


    def transitive_closure(self, term_id_list):

        visited = set(term_id_list)
        unvisited = set()
        edges = set()
        roots = set()

        for term_id in term_id_list:
            rels = self.get_term(term_id).relationships
            unvisited.update(rels)
            edges.update( (term_id, r[0], r[1]) for r in rels )

        while unvisited:
            u = unvisited.pop()
            visited.add(u[1])

            rels = self.get_term(u[1]).relationships
            if not rels:
                roots.add(u[1])
            for rtype, rval in rels:
                if u[0] == 'is_a' or rtype == 'is_a' or \
                  rtype in self.typedefs[u[0]].get('transitive_over', set()):
                    unvisited.add((rtype, rval))
                    edges.add( (u[1], rtype, rval) )

        return visited, edges


    def all_terms_transitive_closure(self):

        tc = dict((k, self.transitive_closure([k])[0]) \
                  for k in self.index2terms)
        return tc


    def as_graph(self, transpose_links=False):

        G = DirectedGraph()
        if transpose_links:
            insert_edge = lambda a, b: G.insert_edge(b, a, 1.0)
        else:
            insert_edge = lambda a, b: G.insert_edge(a, b, 1.0)

        for term_id in self.index2terms:
            rels = self.get_term(term_id).relationships
            for r in rels:
                insert_edge(term_id, r[1])
        return G
