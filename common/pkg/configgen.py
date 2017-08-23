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

CONFIG_ATTRS = ['org_prefix', 'short_species', 'long_species',
                'group', 'tax_id']
CONFIG_DATA = [('sce', 'S. cerevisiae', 'Saccharomyces_cerevisiae',
                'Fungi', 559292),
               ('dre', 'D. rerio', 'Danio_rerio',
                'Non-mammalian_vertebrates', 7955),
               ('pfa', 'P. falciparum', 'Plasmodium_falciparum',
                'Protozoa', 36329),
               ('ath', 'A. thaliana', 'Arabidopsis_thaliana',
                'Plants', 3702),
               ('dme', 'D. melanogaster', 'Drosophila_melanogaster',
                'Invertebrates', 7227),
               ('rno', 'R. norvegicus', 'Rattus_norvegicus',
                'Mammalia', 10116),
               ('cel', 'C. elegans', 'Caenorhabditis_elegans',
                'Invertebrates', 6239),
               ('hsa', 'H. sapiens', 'Homo_sapiens',
                'Mammalia', 9606),
               ('mmu', 'M. musculus', 'Mus_musculus',
                'Mammalia', 10090),
    ]

GO_NAMESPACES = [("biological_process", 'bp'),
                 ("cellular_component", 'cc'),
                 ("molecular_function", 'mf')]

HEAD = \
"""{
  "dep_list": [
"""

TAIL = \
"""    [
      ["name", "all"],
      ["docstring", "'All' special case."],
      ["dep_node_module", "qmbpmn.common.pkg.gluelib"],
      ["dep_node_class", "DepNode"],
      ["hidden", true],
      ["prereqs", null],
      ["args", {}]
    ]
  ]
}
"""

SINGLETONS = \
"""    [
      ["name", "gene2go"],
      ["docstring", "gene2go file."],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_common"],
      ["dep_node_class", "DepURLFile"],
      ["hidden", true],
      ["prereqs", null],
      ["args", {
        "url_fmt": "ftp://ftp.ncbi.nlm.nih.gov/gene/DATA/{0}",
        "path": "gene2go",
        "url_params": ["gene2go.gz"],
        "compression": ".gz",
        "file_name": "gene2go"
      }]
    ],
    [
      ["name", "GO-obo"],
      ["docstring", "Gene Ontology .obo file."],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_common"],
      ["dep_node_class", "DepURLFile"],
      ["hidden", true],
      ["prereqs", null],
      ["args", {
        "url_fmt": "http://www.geneontology.org/ontology/obo_format_1_2/{0}",
        "path": "gene_ontology.1_2.obo",
        "url_params": ["gene_ontology.1_2.obo"],
        "file_name": "gene_ontology.1_2.obo"
      }]
    ],
    [
      ["name", "kegg-brite-pathways"],
      ["docstring", "Describes the hiearchy of terms."],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_common"],
      ["dep_node_class", "DepURLFile"],
      ["hidden", true],
      ["prereqs", null],
      ["args", {
        "url_fmt": "ftp://ftp.genome.jp/pub/kegg/brite/br/{0}",
        "path": "br08901.keg",
        "url_params": ["br08901.keg"],
        "file_name": "br08901.keg"
      }]
    ],
    [
      ["name", "biogrid-ncbi-tab"],
      ["docstring", "The biogrid NCBI file."],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_common"],
      ["dep_node_class", "DepURLFile"],
      ["hidden", true],
      ["prereqs", null],
      ["args", {
        "url_fmt": "http://www.thebiogrid.org/downloads/datasets/{0}",
        "path": "NCBI.tab.txt",
        "url_params": ["NCBI.tab.txt"],
        "file_name": "NCBI.tab.txt"
      }]
    ],
"""


NCBI_GENE_CONFIG_FMT = \
"""    [
      ["name", "ncbi-gene-%(org_prefix)s"],
      ["docstring", "NCBI Gene info for %(short_species)s."],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_common"],
      ["dep_node_class", "DepURLFile"],
      ["hidden", true],
      ["prereqs", null],
      ["args", {
        "url_fmt": "ftp://ftp.ncbi.nih.gov/gene/DATA/GENE_INFO/%(group)s/{0}",
        "path": "%(long_species)s.gene_info",
        "url_params": ["%(long_species)s.gene_info.gz"],
        "compression": ".gz",
        "file_name": "%(long_species)s.gene_info"
      }]
    ],
"""

NCBI_GENE_INDEX_CONFIG_FMT = \
"""    [
      ["name", "ncbi-gene-index-%(org_prefix)s"],
      ["docstring", "Binary index of ncbi-gene-%(org_prefix)s"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_ncbi_gene"],
      ["dep_node_class", "DepNCBIIndex"],
      ["hidden", true],
      ["prereqs", ["ncbi-gene-%(org_prefix)s"]],
      ["args", {
        "gene_info_file": "%(long_species)s.gene_info",
        "gene_info_index": "%(long_species)s.gene_info.ix",
        "tax_id": "%(tax_id)s"
      }]
    ],
"""

KEGG_TERM_FMT = \
"""    [
      ["name", "kegg-term-%(org_prefix)s"],
      ["docstring", "KEGG term mappings for %(short_species)s"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_common"],
      ["dep_node_class", "DepURLFile"],
      ["hidden", true],
      ["prereqs", null],
      ["args", {
        "url_fmt": "ftp://ftp.genome.jp/pub/kegg/pathway/organisms/{0}/{1}",
        "path": "%(org_prefix)s.list",
        "url_params": ["%(org_prefix)s", "%(org_prefix)s.list"],
        "file_name": "%(org_prefix)s.list"
      }]
    ],
"""

ETD_COMBINED_FMT = \
"""    [
      ["name", "ETD-%(org_prefix)s"],
      ["docstring", "GO + KEGG Database: %(short_species)s"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_termdb"],
      ["dep_node_class", "DepCombinedETD"],
      ["hidden", false],
      ["prereqs", [
        "gene2go",
        "GO-obo",
        "ncbi-gene-%(org_prefix)s",
        "kegg-term-%(org_prefix)s",
        "kegg-brite-pathways"
      ]],
      ["args", {
        "storage_dir": "ETD/",
        "kwopts": {
          "output_file": "%(long_species)s.etd",
          "gene2go_file": "gene2go",
          "db_name": "GO + KEGG: %(full_species)s",
          "gene_info_file": "%(long_species)s.gene_info",
          "obo_file": "gene_ontology.1_2.obo",
          "gene2kegg_file": "%(org_prefix)s.list",
          "bri_file": "br08901.keg",
          "org_prefix": "%(org_prefix)s",
          "tax_id": "%(tax_id)s"
        }
      }]
    ],
"""

GO_GMT_FMT = \
"""    [
      ["name", "GO-%(namespace_short)s-%(org_prefix)s.gmt"],
      ["docstring", "GMT formatted GO (%(namespace_short)s): %(short_species)s"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_termdb"],
      ["dep_node_class", "DepGO2Gmt"],
      ["hidden", true],
      ["prereqs", [
        "gene2go",
        "GO-obo",
        "ncbi-gene-%(org_prefix)s"
      ]],
      ["args", {
        "storage_dir": "GMT/",
        "kwopts": {
          "output_file": "GO-%(namespace_short)s-%(org_prefix)s.gmt",
          "gene_info_file": "%(long_species)s.gene_info",
          "obo_file": "gene_ontology.1_2.obo",
          "gene2go_file": "gene2go",
          "tax_id": "%(tax_id)s",
          "namespace": "%(namespace_full)s"
        }
      }]
    ],
"""

KEGG_GMT_FMT = \
"""    [
      ["name", "KEGG-%(org_prefix)s.gmt"],
      ["docstring", "GMT formatted KEGG: %(short_species)s"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_termdb"],
      ["dep_node_class", "DepKEGG2Gmt"],
      ["hidden", true],
      ["prereqs", [
        "ncbi-gene-%(org_prefix)s",
        "kegg-term-%(org_prefix)s",
        "kegg-brite-pathways"
      ]],
      ["args", {
        "storage_dir": "GMT/",
        "kwopts": {
          "output_file": "KEGG-%(org_prefix)s.gmt",
          "gene_info_file": "%(long_species)s.gene_info",
          "gene2kegg_file": "%(org_prefix)s.list",
          "bri_file": "br08901.keg",
          "org_prefix": "%(org_prefix)s",
          "tax_id": "%(tax_id)s"
        }
      }]
    ],
"""

ALL_GMT = \
"""    [
      ["name", "gmt-all"],
      ["docstring", "GMT formatted - all."],
      ["dep_node_module", "qmbpmn.common.pkg.gluelib"],
      ["dep_node_class", "DepNode"],
      ["hidden", true],
      ["prereqs", [
        "GO-bp-ath.gmt",
        "GO-cc-ath.gmt",
        "GO-mf-ath.gmt",
        "GO-bp-cel.gmt",
        "GO-cc-cel.gmt",
        "GO-mf-cel.gmt",
        "GO-bp-dre.gmt",
        "GO-cc-dre.gmt",
        "GO-mf-dre.gmt",
        "GO-bp-dme.gmt",
        "GO-cc-dme.gmt",
        "GO-mf-dme.gmt",
        "GO-bp-hsa.gmt",
        "GO-cc-hsa.gmt",
        "GO-mf-hsa.gmt",
        "GO-bp-mmu.gmt",
        "GO-cc-mmu.gmt",
        "GO-mf-mmu.gmt",
        "GO-bp-pfa.gmt",
        "GO-cc-pfa.gmt",
        "GO-mf-pfa.gmt",
        "GO-bp-rno.gmt",
        "GO-cc-rno.gmt",
        "GO-mf-rno.gmt",
        "GO-bp-sce.gmt",
        "GO-cc-sce.gmt",
        "GO-mf-sce.gmt",
        "KEGG-ath.gmt",
        "KEGG-cel.gmt",
        "KEGG-dre.gmt",
        "KEGG-dme.gmt",
        "KEGG-hsa.gmt",
        "KEGG-mmu.gmt",
        "KEGG-pfa.gmt",
        "KEGG-rno.gmt",
        "KEGG-sce.gmt"
      ]],
      ["args", {}]
    ],
"""

NETWORKS = \
"""    [
      ["name", "hsa-full-network"],
      ["docstring", "ITM Probe Network: H. sapiens (full)"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_network"],
      ["dep_node_class", "DepITMProbeNetwork"],
      ["hidden", false],
      ["prereqs", ["ncbi-gene-index-hsa", "biogrid-ncbi-tab"]],
      ["args", {
        "org_name": "Homo_sapiens",
        "termdb_dir": "ETD/",
        "graph_params": [{
          "network_file": "Homo_sapiens.Fnet.cfg",
          "graph_file": "Homo_sapiens.Fnet.pkl",
          "biogrid_file": "NCBI.tab.txt",
          "gene_info_index": "Homo_sapiens.gene_info.ix",
          "network_name_suffix": "Homo sapiens - Full",
          "group_name": "Other Physical Interaction",
          "antisinks": [],
          "non_filtered_pubmed_ids": null,
          "undirected_systems_map": {
            "Co-fractionation": 1.0,
            "Biochemical Activity": 1.0,
            "Affinity Capture-Western": 1.0,
            "Far Western": 1.0,
            "Reconstituted Complex": 1.0,
            "Two-hybrid": 1.0,
            "Co-crystal Structure": 1.0,
            "Co-purification": 1.0,
            "Co-localization": 1.0,
            "Affinity Capture-RNA": 1.0,
            "PCA": 1.0,
            "Affinity Capture-MS": 1.0,
            "FRET": 1.0
          },
          "throughput_cutoff": 300000000,
          "directed_systems_map": {}
        }]
      }]
    ],
    [
      ["name", "dme-full-network"],
      ["docstring", "ITM Probe Network: D. melanogaster (full)"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_network"],
      ["dep_node_class", "DepITMProbeNetwork"],
      ["hidden", false],
      ["prereqs", ["ncbi-gene-index-dme", "biogrid-ncbi-tab"]],
      ["args", {
        "org_name": "Drosophila_melanogaster",
        "termdb_dir": "ETD/",
        "graph_params": [{
          "network_file": "Drosophila_melanogaster.Fnet.cfg",
          "graph_file": "Drosophila_melanogaster.Fnet.pkl",
          "biogrid_file": "NCBI.tab.txt",
          "gene_info_index": "Drosophila_melanogaster.gene_info.ix",
          "network_name_suffix": "Drosophila melanogaster - Full",
          "group_name": "Other Physical Interaction",
          "antisinks": [],
          "non_filtered_pubmed_ids": null,
          "directed_systems_map": {},
          "throughput_cutoff": 300000000,
          "undirected_systems_map": {
            "Co-fractionation": 1.0,
            "Biochemical Activity": 1.0,
            "Affinity Capture-Western": 1.0,
            "Far Western": 1.0,
            "Reconstituted Complex": 1.0,
            "Two-hybrid": 1.0,
            "Co-crystal Structure": 1.0,
            "Co-purification": 1.0,
            "Co-localization": 1.0,
            "Affinity Capture-RNA": 1.0,
            "PCA": 1.0,
            "Affinity Capture-MS": 1.0,
            "FRET": 1.0
          }
        }]
      }]
    ],
    [
      ["name", "cel-full-network"],
      ["docstring", "ITM Probe Network: C. elegans (full)"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_network"],
      ["dep_node_class", "DepITMProbeNetwork"],
      ["hidden", false],
      ["prereqs", ["ncbi-gene-index-cel", "biogrid-ncbi-tab"]],
      ["args", {
        "org_name": "Caenorhabditis_elegans",
        "termdb_dir": "ETD/",
        "graph_params": [{
          "network_file": "Caenorhabditis_elegans.Fnet.cfg",
          "graph_file": "Caenorhabditis_elegans.Fnet.pkl",
          "biogrid_file": "NCBI.tab.txt",
          "gene_info_index": "Caenorhabditis_elegans.gene_info.ix",
          "network_name_suffix": "Caenorhabditis_elegans - Full",
          "group_name": "Other Physical Interaction",
          "antisinks": [],
          "throughput_cutoff": 300000000,
          "directed_systems_map": {},
          "non_filtered_pubmed_ids": null,
          "undirected_systems_map": {
            "Co-fractionation": 1.0,
            "Biochemical Activity": 1.0,
            "Affinity Capture-Western": 1.0,
            "Far Western": 1.0,
            "Reconstituted Complex": 1.0,
            "Two-hybrid": 1.0,
            "Co-crystal Structure": 1.0,
            "Co-purification": 1.0,
            "Co-localization": 1.0,
            "Affinity Capture-RNA": 1.0,
            "PCA": 1.0,
            "Affinity Capture-MS": 1.0,
            "FRET": 1.0
          }
        }]
      }]
    ],
    [
      ["name", "sce-full-network"],
      ["docstring", "ITM Probe Network: S. cerevisiae (full)"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_network"],
      ["dep_node_class", "DepITMProbeNetwork"],
      ["hidden", false],
      ["prereqs", ["ncbi-gene-index-sce", "biogrid-ncbi-tab"]],
      ["args", {
        "org_name": "Saccharomyces_cerevisiae",
        "termdb_dir": "ETD/",
        "graph_params": [{
          "graph_file": "Saccharomyces_cerevisiae.Fnet.pkl",
          "directed_systems_map": {},
          "group_name": "Yeast Physical Interaction",
          "biogrid_file": "NCBI.tab.txt",
          "network_name_suffix": "Saccharomyces cerevisiae - Full",
          "gene_info_index": "Saccharomyces_cerevisiae.gene_info.ix",
          "network_file": "Saccharomyces_cerevisiae.Fnet.cfg",
          "non_filtered_pubmed_ids": ["17200106", "18467557"],
          "undirected_systems_map": {
            "Co-fractionation": 1.0,
            "Biochemical Activity": 1.0,
            "Affinity Capture-Western": 1.0,
            "Far Western": 1.0,
            "Reconstituted Complex": 1.0,
            "Two-hybrid": 1.0,
            "Co-crystal Structure": 1.0,
            "Co-purification": 1.0,
            "Co-localization": 1.0,
            "Affinity Capture-RNA": 1.0,
            "PCA": 1.0,
            "Affinity Capture-MS": 1.0,
            "FRET": 1.0
          },
          "throughput_cutoff": 300000000,
          "antisinks": ["CSE4", "HHF1", "HHF2", "HHO1", "HHT1", "HHT2", "HTA1", "HTA2", "HTB1",
          "HTB2", "NAP1", "APJ1", "ATP11", "BTT1", "CCT2", "CCT3", "CCT4", "CCT5", "CCT6",
          "CCT7", "CCT8", "CDC37", "CNE1", "COX20", "CPR6", "CPR7", "EGD1", "EGD2", "HSC82",
          "HSP10", "HSP26", "HSP31", "HSP32", "HSP33", "HSP42", "HSP78", "HSP82", "JEM1", "KAR2",
          "LHS1", "MCX1", "MDJ1", "MGE1", "MRS11", "PAM18", "PET100", "PFD1", "PNO1", "RFM1",
          "SHR3", "SHY1", "SIS1", "SNO4", "SSA1", "SSA2", "SSA3", "SSA4", "SSB1", "SSB2",
          "SSQ1", "SSZ1", "TCM62", "TCP1", "TIM9", "TSA1", "VMA22", "VPS45", "YDJ1", "ZUO1",
          "ACT1", "ARC18", "ARC40", "ARP1", "ARP10", "ARP2", "ARP3", "ASK1", "BBP1", "BIM1",
          "CDC10", "CDC11", "CDC12", "CDC3", "CDC31", "CNM67", "DAD1", "DAD2", "DAM1", "DUO1",
          "FIN1", "JNM1", "KIP1", "MDM1", "MHP1", "MPS2", "NDC1", "NUD1", "NUF2", "SHS1",
          "SPC105", "SPC110", "SPC19", "SPC24", "SPC25", "SPC29", "SPC34", "SPC42", "SPC72", "SPC97",
          "SPC98", "SPR28", "SPR3", "STU1", "STU2", "TID3", "TUB1", "TUB2", "TUB3", "TUB4",
          "YOR129C", "MYO1", "MYO2", "MYO3", "MYO4", "MYO5", "ABP140", "ALF1", "ARC15", "ASE1",
          "ATG4", "ATG8", "BBC1", "BIK1", "BNI1", "BNR1", "BUD6", "CAP1", "CAP2", "CIN1",
          "CRN1", "DLD2", "GCS1", "GIM3", "GIM4", "GIM5", "HOF1", "IQG1", "LAS17", "MLC1",
          "MLC2", "NIP100", "NUM1", "PAC10", "PAC2", "PEA2", "PFY1", "RBL2", "RVS161", "RVS167",
          "SAC6", "SCP1", "SHE4", "SLA1", "SPA2", "SPH1", "SRV2", "TPM1", "TPM2", "TWF1",
          "VRP1", "YKE2", "HTZ1"]
        }]
      }]
    ],
    [
      ["name", "sce-directed-network"],
      ["docstring", "ITM Probe Network: S. cerevisiae (directed)"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_network"],
      ["dep_node_class", "DepITMProbeNetwork"],
      ["hidden", false],
      ["prereqs", ["ncbi-gene-index-sce", "biogrid-ncbi-tab"]],
      ["args", {
        "org_name": "Saccharomyces_cerevisiae",
        "termdb_dir": "ETD/",
        "graph_params": [{
          "biogrid_file": "NCBI.tab.txt",
          "non_filtered_pubmed_ids": ["17200106", "18467557"],
          "undirected_systems_map": {
            "Co-fractionation": 1.0,
            "Two-hybrid": 1.0,
            "Far Western": 1.0,
            "Reconstituted Complex": 1.0,
            "Affinity Capture-Western": 1.0,
            "Co-crystal Structure": 1.0,
            "Co-purification": 1.0,
            "Co-localization": 1.0,
            "Affinity Capture-RNA": 1.0,
            "PCA": 1.0,
            "Affinity Capture-MS": 1.0,
            "FRET": 1.0
          },
          "gene_info_index": "Saccharomyces_cerevisiae.gene_info.ix",
          "network_file": "Saccharomyces_cerevisiae.Dnet.cfg",
          "throughput_cutoff": 300,
          "antisinks": ["CSE4", "HHF1", "HHF2", "HHO1", "HHT1", "HHT2", "HTA1", "HTA2", "HTB1",
          "HTB2", "NAP1", "APJ1", "ATP11", "BTT1", "CCT2", "CCT3", "CCT4", "CCT5", "CCT6",
          "CCT7", "CCT8", "CDC37", "CNE1", "COX20", "CPR6", "CPR7", "EGD1", "EGD2", "HSC82",
          "HSP10", "HSP26", "HSP31", "HSP32", "HSP33", "HSP42", "HSP78", "HSP82", "JEM1", "KAR2",
          "LHS1", "MCX1", "MDJ1", "MGE1", "MRS11", "PAM18", "PET100", "PFD1", "PNO1", "RFM1",
          "SHR3", "SHY1", "SIS1", "SNO4", "SSA1", "SSA2", "SSA3", "SSA4", "SSB1", "SSB2",
          "SSQ1", "SSZ1", "TCM62", "TCP1", "TIM9", "TSA1", "VMA22", "VPS45", "YDJ1", "ZUO1",
          "ACT1", "ARC18", "ARC40", "ARP1", "ARP10", "ARP2", "ARP3", "ASK1", "BBP1", "BIM1",
          "CDC10", "CDC11", "CDC12", "CDC3", "CDC31", "CNM67", "DAD1", "DAD2", "DAM1", "DUO1",
          "FIN1", "JNM1", "KIP1", "MDM1", "MHP1", "MPS2", "NDC1", "NUD1", "NUF2", "SHS1",
          "SPC105", "SPC110", "SPC19", "SPC24", "SPC25", "SPC29", "SPC34", "SPC42", "SPC72", "SPC97",
          "SPC98", "SPR28", "SPR3", "STU1", "STU2", "TID3", "TUB1", "TUB2", "TUB3", "TUB4",
          "YOR129C", "MYO1", "MYO2", "MYO3", "MYO4", "MYO5", "ABP140", "ALF1", "ARC15", "ASE1",
          "ATG4", "ATG8", "BBC1", "BIK1", "BNI1", "BNR1", "BUD6", "CAP1", "CAP2", "CIN1",
          "CRN1", "DLD2", "GCS1", "GIM3", "GIM4", "GIM5", "HOF1", "IQG1", "LAS17", "MLC1",
          "MLC2", "NIP100", "NUM1", "PAC10", "PAC2", "PEA2", "PFY1", "RBL2", "RVS161", "RVS167",
          "SAC6", "SCP1", "SHE4", "SLA1", "SPA2", "SPH1", "SRV2", "TPM1", "TPM2", "TWF1",
          "VRP1", "YKE2", "HTZ1"],
          "graph_file": "Saccharomyces_cerevisiae.Dnet.pkl",
          "directed_systems_map": {
            "Biochemical Activity": 2.0
          },
          "group_name": "Yeast Physical Interaction",
          "network_name_suffix": "Saccharomyces cerevisiae - Directed"
        }]
      }]
    ],
    [
      ["name", "sce-reduced-network"],
      ["docstring", "ITM Probe Network: S. cerevisiae (reduced)"],
      ["dep_node_module", "qmbpmn.common.pkg.depnode_network"],
      ["dep_node_class", "DepITMProbeNetwork"],
      ["hidden", false],
      ["prereqs", ["ncbi-gene-index-sce", "biogrid-ncbi-tab"]],
      ["args", {
        "org_name": "Saccharomyces_cerevisiae",
        "termdb_dir": "ETD/",
        "graph_params": [{
          "biogrid_file": "NCBI.tab.txt",
          "non_filtered_pubmed_ids": ["17200106", "18467557"],
          "undirected_systems_map": {
            "Co-fractionation": 1.0,
            "Biochemical Activity": 1.0,
            "Affinity Capture-Western": 1.0,
            "Far Western": 1.0,
            "Reconstituted Complex": 1.0,
            "Two-hybrid": 1.0,
            "Co-crystal Structure": 1.0,
            "Co-purification": 1.0,
            "Co-localization": 1.0,
            "Affinity Capture-RNA": 1.0,
            "PCA": 1.0,
            "Affinity Capture-MS": 1.0,
            "FRET": 1.0
          },
          "gene_info_index": "Saccharomyces_cerevisiae.gene_info.ix",
          "network_file": "Saccharomyces_cerevisiae.Rnet.cfg",
          "throughput_cutoff": 300,
          "antisinks": ["CSE4", "HHF1", "HHF2", "HHO1", "HHT1", "HHT2", "HTA1", "HTA2", "HTB1",
          "HTB2", "NAP1", "APJ1", "ATP11", "BTT1", "CCT2", "CCT3", "CCT4", "CCT5", "CCT6",
          "CCT7", "CCT8", "CDC37", "CNE1", "COX20", "CPR6", "CPR7", "EGD1", "EGD2", "HSC82",
          "HSP10", "HSP26", "HSP31", "HSP32", "HSP33", "HSP42", "HSP78", "HSP82", "JEM1", "KAR2",
          "LHS1", "MCX1", "MDJ1", "MGE1", "MRS11", "PAM18", "PET100", "PFD1", "PNO1", "RFM1",
          "SHR3", "SHY1", "SIS1", "SNO4", "SSA1", "SSA2", "SSA3", "SSA4", "SSB1", "SSB2",
          "SSQ1", "SSZ1", "TCM62", "TCP1", "TIM9", "TSA1", "VMA22", "VPS45", "YDJ1", "ZUO1",
          "ACT1", "ARC18", "ARC40", "ARP1", "ARP10", "ARP2", "ARP3", "ASK1", "BBP1", "BIM1",
          "CDC10", "CDC11", "CDC12", "CDC3", "CDC31", "CNM67", "DAD1", "DAD2", "DAM1", "DUO1",
          "FIN1", "JNM1", "KIP1", "MDM1", "MHP1", "MPS2", "NDC1", "NUD1", "NUF2", "SHS1",
          "SPC105", "SPC110", "SPC19", "SPC24", "SPC25", "SPC29", "SPC34", "SPC42", "SPC72", "SPC97",
          "SPC98", "SPR28", "SPR3", "STU1", "STU2", "TID3", "TUB1", "TUB2", "TUB3", "TUB4",
          "YOR129C", "MYO1", "MYO2", "MYO3", "MYO4", "MYO5", "ABP140", "ALF1", "ARC15", "ASE1",
          "ATG4", "ATG8", "BBC1", "BIK1", "BNI1", "BNR1", "BUD6", "CAP1", "CAP2", "CIN1",
          "CRN1", "DLD2", "GCS1", "GIM3", "GIM4", "GIM5", "HOF1", "IQG1", "LAS17", "MLC1",
          "MLC2", "NIP100", "NUM1", "PAC10", "PAC2", "PEA2", "PFY1", "RBL2", "RVS161", "RVS167",
          "SAC6", "SCP1", "SHE4", "SLA1", "SPA2", "SPH1", "SRV2", "TPM1", "TPM2", "TWF1",
          "VRP1", "YKE2", "HTZ1"],
          "graph_file": "Saccharomyces_cerevisiae.Rnet.pkl",
          "directed_systems_map": {},
          "group_name": "Yeast Physical Interaction",
          "network_name_suffix": "Saccharomyces cerevisiae - Reduced"
        }]
      }]
    ],
"""


def _attrs_dict(item):
    d = dict(zip(CONFIG_ATTRS, item))
    d['full_species'] = ' '.join(d['long_species'].split('_'))
    return d


def write_config_options(fp=sys.stdout):
    """
    Writes current config options for cutting and pasting into
    dep_config.json
    """

    fp.write(HEAD)
    fp.write(SINGLETONS)
    for item in CONFIG_DATA:
        s = NCBI_GENE_CONFIG_FMT % _attrs_dict(item)
        fp.write(s)
        s = NCBI_GENE_INDEX_CONFIG_FMT % _attrs_dict(item)
        fp.write(s)
        s = KEGG_TERM_FMT % _attrs_dict(item)
        fp.write(s)
        s = ETD_COMBINED_FMT % _attrs_dict(item)
        fp.write(s)
        s = KEGG_GMT_FMT % _attrs_dict(item)
        fp.write(s)
        for full_ns, short_ns in GO_NAMESPACES:
            d = _attrs_dict(item)
            d.update([('namespace_short', short_ns),
                      ('namespace_full', full_ns)])
            s = GO_GMT_FMT % d
            fp.write(s)
    fp.write(ALL_GMT)
    fp.write(NETWORKS)
    fp.write(TAIL)

if __name__ == "__main__":
    write_config_options()
