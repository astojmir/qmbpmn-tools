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


import os.path
from collections import defaultdict
from .tab_file import TabFileParser
from .ncbi_gene import NCBIGenes_from_index
from ..graph.csrgraph import CSRDirectedGraph
from ..graph.digraph import DirectedGraph
from ...web.ITMProbe.network import ITMProbeNetwork
from ..utils.dataobj import save_data_object

NODE_URL_FMT = "http://www.ncbi.nlm.nih.gov/sites/entrez?db=gene" \
               "&cmd=Retrieve&dopt=Graphics&list_uids=%(gene_id)s"

GENETIC_INTERACTIONS = set(['Dosage Growth Defect', 'Dosage Lethality',
                            'Dosage Rescue', 'Synthetic Growth Defect',
                            'Synthetic Lethality', 'Synthetic Rescue',
                             'Phenotypic Enhancement', 'Phenotypic Suppression'])
PHYSICAL_INTERACTIONS = set(['Affinity Capture-MS', #'Affinity Capture-RNA',
                             'Affinity Capture-Western',
                             'Co-crystal Structure', 'Co-fractionation',
                             'Co-localization', 'Co-purification', 'FRET',
                             'Far Western', 'Reconstituted Complex',
                             'Two-hybrid', 'PCA'])
BIOCHEMICAL_INTERACTIONS = set(['Biochemical Activity'])
MISC_INTERACTIONS = set(['Protein-RNA', 'Protein-peptide'])

class BioGRIDParser3(object):
    """
    Load the graph from a tab-separated file in the BioGRID (NCBI Gene) format.
    Keep additional data.
    """

    def __init__(self,
                 biogrid_file,
                 gene_info_index,
                 undirected_systems_map,
                 directed_systems_map,
                 throughput_cutoff=300,
                 non_filtered_pubmed_ids=None):

        with open(gene_info_index, 'r') as fp:
            self.genes = NCBIGenes_from_index(fp)
        self.interactions = defaultdict(list)
        self.directed_interactions = defaultdict(list)
        self.accepted_directed_pairs = set()
        self.experimental_systems = defaultdict(int)
        self.pub_counts = defaultdict(int)

        self.undirected_systems_map = undirected_systems_map
        self.directed_systems_map = directed_systems_map
        self.throughput_cutoff = throughput_cutoff

        self.non_filtered_pubmed_ids = set() if non_filtered_pubmed_ids is None \
                                             else set(non_filtered_pubmed_ids)

        self.gene_id2symb = dict((self.genes.gene_ids[i], smb) \
          for i, smb in enumerate(self.genes.symbols))

        # Parse the 'NCBI.tab.txt' file
        with open(biogrid_file, 'rb') as fp:

            self.biogrid_version = fp.next().split(':')[1].strip()
            for line in fp:
                self._line_scanner(line.strip().split('\t'))


    def _line_scanner(self, fields):

        gene_id1 = int(fields[0])
        gene_id2 = int(fields[1])
        biogrid_id1 = int(fields[2])
        biogrid_id2 = int(fields[3])
        exp_sys = fields[4]
        pubmed_id = int(fields[5])

        self.pub_counts[pubmed_id] += 1

        # Initial filters: genes database, experimental systems
        if (gene_id1 not in self.genes.gene_id2index) or \
           (gene_id2 not in self.genes.gene_id2index) or \
           ((exp_sys not in self.undirected_systems_map) and \
            (exp_sys not in self.directed_systems_map)):
            return None

        # Add all data
        self.experimental_systems[exp_sys] += 1

        node1 = self.gene_id2symb[gene_id1]
        node2 = self.gene_id2symb[gene_id2]
        pair = (node1, node2)

        if exp_sys in self.undirected_systems_map:
            if (node2, node1) in self.interactions:
                pair = (node2, node1)
            self.interactions[pair].append((exp_sys, pubmed_id))
        elif exp_sys in self.directed_systems_map:
            self.directed_interactions[pair].append((exp_sys, pubmed_id))


    def filter_by_throughput3(self, pair, interaction_data):

        if len(interaction_data) > 1:
            return True
        pubmed_id = interaction_data[0][1]
        if pubmed_id in self.non_filtered_pubmed_ids or \
           self.pub_counts[pubmed_id] <= self.throughput_cutoff:
            return True
        return False


    def filter_undirected_in_directed(self, pair):
        # FILTER ALL UNDIRECTED INTERACTIONS THAT HAVE A CORRESPONDING DIRECTED ONE
        p1, p2 = pair
        if (p1,p2) in self.accepted_directed_pairs or \
           (p2,p1) in self.accepted_directed_pairs:
            return False
        return True

    def filter_undirected(self, pair, interaction_data):
        """
        Filter for undirected interactions.
        """
        return self.filter_undirected_in_directed(pair) and \
               self.filter_by_throughput3(pair, interaction_data)


    def filter_directed(self, pair, interaction_data):
        """
        Filter for directed interactions.
        """
        return self.filter_by_throughput3(pair, interaction_data)


    def get_graph(self, graph_class):

        G = graph_class()

        # Filter interactions and insert edges
        if len(self.directed_systems_map):
            directed_weight = self.directed_systems_map.values()[0]
            for pair, interaction_data in self.directed_interactions.iteritems():
                if self.filter_directed(pair, interaction_data):
                    self.accepted_directed_pairs.add(pair)
                    G.insert_edge(pair[0], pair[1], directed_weight)

        undirected_weight = self.undirected_systems_map.values()[0]
        for pair, interaction_data in self.interactions.iteritems():
            if self.filter_undirected(pair, interaction_data):
                G.insert_edge(pair[0], pair[1], undirected_weight)
                G.insert_edge(pair[1], pair[0], undirected_weight)

        return G







def create_network(dest_path, network_file, graph_file, biogrid_file,
                   gene_info_index, network_name_suffix='', group_name='All',
                   enrich_files=None, antisinks=None, **kwargs):

    prs = BioGRIDParser3(biogrid_file, gene_info_index, **kwargs)
    G1 = prs.get_graph(DirectedGraph)
    network_name = 'BioGRID-%s %s' % (prs.biogrid_version,
                                      network_name_suffix)

    G2 = CSRDirectedGraph(G1._adjacency_matrix, G1.nodes)
    graph_path = os.path.join(dest_path, graph_file)
    with open(graph_path, 'wb') as fp:
        G2.tofile(fp)

    enrich_files = [] if enrich_files is None else enrich_files

    config_opts = [['network_name', network_name],
                   ['graph_file', graph_file],
                   ['group_name', group_name],
                   ['gene_info_index', os.path.basename(gene_info_index)],
                   ['node_url_fmt', NODE_URL_FMT],
                   ['enrich_files', enrich_files],
                   ['antisinks', []],
                   ]

    network_path = os.path.join(dest_path, network_file)
    save_data_object(config_opts, network_path)

    # Now update antisinks so that we don't get any warnings for default
    # antisinks
    if antisinks is not None:
        network = ITMProbeNetwork(network_path)
        new_antisinks = network.validate_symbols(antisinks, '', True)
        config_opts[-1] = ['antisinks', new_antisinks]
        save_data_object(config_opts, network_path)

    return [network_path, graph_path]
