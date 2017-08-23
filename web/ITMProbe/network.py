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
import os.path
from collections import defaultdict
from ...common.graph.csrgraph import CSRDirectedGraph
from ...common.db_parsers.ncbi_gene import NCBIGenes_from_index
from ...common.utils.dataobj import restore_data_object
from .. import exceptions as exc
from ..SaddleSum import get_etd_info


class ITMProbeNetwork(object):

    WARNING_FMTS = ['%(field)s: Specified network does not contain entity'
                      ' "%(id)s"%(suffix)s.',
                    '%(field)s: Identifier %(id)s is'
                      ' also a synonym for %(aliases)s.',
                    '%(field)s: %(id)s is an alias for entities'
                      '%(aliases)s while not being a primary identifier for any'
                      '%(suffix)s.',
                    '%(field)s: Entity %(id)s was previously specified as'
                      ' %(aliases)s (additional instance IGNORED).',
                    ]

    def __init__(self, network_file, init_data=True):

        self.network_file = network_file
        self.init_data = init_data

        self._init_attrs()
        if init_data:
            self._init_data()

    def __getstate__(self):

        return {'network_file': self.network_file,
                'init_data': self.init_data}

    def __setstate__(self, state):

        self.__dict__ = state
        self._init_attrs()
        if self.init_data:
            self._init_data()

    def _init_attrs(self):

        self.gene_dir = self.graph_dir = os.path.split(self.network_file)[0]
        self.G = self.genes = None

        config_opts = restore_data_object(self.network_file)
        self.__dict__.update(config_opts)
        self.enrich_files.sort()

    def _init_data(self):

        graph_path = os.path.join(self.graph_dir, self.graph_file)
        with open(graph_path, 'rb') as fp:
            self.G = CSRDirectedGraph(fp)
        self.G.filename = graph_path
        self.warning_messages = []
        self.open_genes()

    def open_genes(self):

        gene_ix_path = os.path.join(self.gene_dir, self.gene_info_index)
        with open(gene_ix_path, 'rb') as fp:
            self.genes = NCBIGenes_from_index(fp)

    def get_network_node(self, gene_index):
        if gene_index is None:
            return None
        smb = self.genes.symbols[gene_index]
        tested_symbols = [str(self.genes.gene_ids[gene_index]), smb] + \
                         self.genes.symbol2aliases[smb]
        node = None
        for p in tested_symbols:
            if self.G.has_node(p):
                node = p
                break
        return node

    def validate_symbols(self, symbols, field, ignore_unknown=False):

        mapped_symb, _ = self.genes.map_symbols(symbols)
        valid_ids = []
        warnings = []

        for smb, item in zip(symbols, mapped_symb):
            gene_index, warn = item
            node = self.get_network_node(gene_index)
            if node is not None:
                if (warn is None or warn[1] != self.genes.DUPLICATE_ID):
                    valid_ids.append(node)
            elif not ignore_unknown:
                warn = (smb, self.genes.UNKNOWN_ID,
                        {'field': field,
                         'suffix': ' All identifiers for boundary nodes'
                                   ' (sources and sinks) must be valid.'})
                msg = self.genes.warning_msgs([warn], set(),
                                              self.WARNING_FMTS)[0]
                raise exc.BadIdentifier(msg)
            else:
                warn = (smb, self.genes.UNKNOWN_ID, {})

            if warn:
                warn[2].update({'field': field, 'suffix': ' (IGNORED)'})
                warnings.append(warn)

        self.warning_messages += self.genes.warning_msgs(warnings,
                                                        set(),
                                                        self.WARNING_FMTS)
        return valid_ids

    def get_enrich_termdb_names(self, cmd_path=None):

        termdb_names = []
        for enrich_file in self.enrich_files:
            etd_file = os.path.join(self.gene_dir, enrich_file)
            etd_info =  get_etd_info(etd_file, cmd_path)
            termdb_names.append(etd_info['db_name'])
        return termdb_names

    def symbol2gene_id(self, symb):

        _, sl = self.genes.map_symbols_to_gene_ids([symb])
        if len(sl):
            return str(sl[0])
        else:
            return None

    def to_sif_file(self, fp=sys.stdout):
        """
        Write network in Cytoscape SIF format.
        """
        gn = self.genes
        nodes = self.G.nodes
        A = self.G.weighted_adjacency_matrix().adjacency_matrix
        geneids = [gn.gene_ids[gn.alias2index[str(node)]] for node in nodes]
        counts = defaultdict(int)

        for i, node in enumerate(nodes):
            for k in xrange(A.indptr[i], A.indptr[i+1]):
                if A.data[k] > 0:
                    j = A.indices[k]
                    if i < j:
                        counts[(i,j)] += 1
                    else:
                        counts[(j,i)] += 1

        for pair, c in counts.iteritems():
            geneid1 = geneids[pair[0]]
            geneid2 = geneids[pair[1]]
            if c == 1:
                fp.write('%d\td\t%d\n' % (geneid1, geneid2))
            else:
                fp.write('%d\tu\t%d\n' % (geneid1, geneid2))
