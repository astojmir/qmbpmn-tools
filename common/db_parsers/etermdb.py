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

"""
Routines for writing extended term database (to be used with standalone
SaddleSum)
"""

import numpy as np
from collections import defaultdict
from ..utils.filesys import write_string_list
from .ncbi_gene import NCBIGenes_from_gene_info
from .ncbi_gene import index_gene_info
from .bri import KEGGOntology
from .obo import OBOntology

EXTERMDB_MAGIC = 1644632861  # crc32('qmbpmn-tools-EXTERMDB')
KEGGTERMDB_MAGIC = -2030228893 # crc32('qmbpmn-tools-KEGGTERMDB')
GOTERMDB_MAGIC = -2107916768 # crc32('qmbpmn-tools-GOTERMDB')

GOTERM_URL_FMT = "http://amigo.geneontology.org/cgi-bin/amigo/" \
                 "term-details?term=%s"
KEGG_LEAF_URL_FMT = "http://www.genome.jp/kegg-bin/show_pathway?" \
                    "org_name=%s&amp;mapno=%s&amp;mapscale=1.0" \
                    "&amp;show_description=show"
KEGG_HIGHER_URL_FMT = "http://www.genome.jp/kegg-bin/get_htext?" \
                      "htext=br08901.keg&amp;filedir=%%2ffiles" \
                      "&amp;extend=&amp;open=%s"


def write_header(fp, db_name, namespaces):
    """Write the header of extended term database"""
    # *** Header section structure ***
    # char start_separator           - 'EXTERMDB'
    # uint32 version_magic           - changes for each different version
    # uint32 db_name_buflen
    # char db_name                   - Full database name (description)
    # uint32 num_namespaces
    # uint32 namespaces_buflen
    # char namespaces_buf            - Names of all namespaces

    fp.write('EXTERMDB')
    fp.write(np.array([EXTERMDB_MAGIC], dtype='<u4'))
    write_string_list(fp, [db_name], False)
    write_string_list(fp, namespaces, True)


def write_namespace(fp, version_magic, edgetype_names, slim_flags, term_hits,
                    term_ids, descriptions, relationships, metadata):
    """Write the terms database plus mappings to genes (single namespace)"""

    # *** Namespace (termdb) section structure ***
    # char start_separator           - 'TERMDBNS'
    # uint32 version_magic           - changes for each different version
    # uint32 num_edgetypes
    # uint32 edgetype_buflen
    # char edgetype_names_bug[]      - names for relationships
    # uint32 M                       - number of terms
    # uint32 slim_flags[M]            - whether the terms are in reduced dataset
    # uint32 num_hits[M]             - counts of hits for each term
    # uint32 hits[M][num_hits]       - hits to genes
    # uint32 termid_buflen
    # char termid_buf[]              - term IDs
    # uint32 desc_buflen
    # char desc_buf[]                - term descriptions
    # num_parents[M]                 - numbers of parents of each term
    # parents[M][num_parents]        - indexes of parents
    # edgetypes[M][num_parents]      - relationships to parents
    # uint32 metadata_buflen
    # char metadata[metadata_buflen] - metadata (provided by the caller)

    fp.write('TERMDBNS')
    fp.write(np.array([version_magic], dtype='<u4'))
    write_string_list(fp, edgetype_names, True)
    fp.write(np.array([len(slim_flags)], dtype='<u4'))
    fp.write(np.array(slim_flags, dtype='<u4'))
    for hits in term_hits:
        fp.write(np.array([len(hits)], dtype='<u4'))
    for hits in term_hits:
        fp.write(np.array(hits, dtype='<u4'))
    write_string_list(fp, term_ids, False)
    write_string_list(fp, descriptions, False)
    for rel_lst in relationships:
        fp.write(np.array([len(rel_lst)], dtype='<u4'))
    for rel_lst in relationships:
        parents = [item[0] for item in rel_lst]
        fp.write(np.array(parents, dtype='<u4'))
    for rel_lst in relationships:
        edge_types = [item[1] for item in rel_lst]
        fp.write(np.array(edge_types, dtype='<u4'))
    write_string_list(fp, metadata, False)


def _filter_term2hits(term2hits):
    return dict(item for item in term2hits.iteritems() \
                if len(item[1]) > 1)

def _kegg_term2hits(gene2kegg_file, org_prefix, genes):
    term2hits = defaultdict(set)
    with open(gene2kegg_file, 'rb') as gene2kegg_fp:
        for line in gene2kegg_fp:
            #We only care about the first two columns right now.
            data = line.split()[:2]
            path_prefix, pathway = data[0].split(':')
            pathway = pathway.replace(org_prefix, '')
            org_prefix2, gene = data[1].split(':')

            # Do not fail silently
            assert (path_prefix == 'path')

            if org_prefix2 != org_prefix:
                continue
            gene_mapped = genes.map_symbols([gene])
            if gene_mapped[0][0][0] is not None:
                # Don't append a gene that could not be found.
                term2hits[pathway].add(gene_mapped[0][0][0])
    return _filter_term2hits(term2hits)


def _kegg_process_namespace(genes, ontology, term2hits):

    termid2index = {}
    slim_flags = []
    term_hits = []
    term_ids = []
    descriptions = []
    parents = []
    relationships = []

    all_terms, _ = ontology.transitive_closure(term2hits.keys())

    # Add root term
    termid2index['KEGG Pathway'] = 0
    slim_flags.append(2) # KEGG root term
    term_hits.append([])
    term_ids.append('KEGG:Pathway')
    descriptions.append('KEGG Pathway Database')
    parents.append(None)

    # First pass
    i = 1
    for term_id in all_terms:
        term = ontology.get_term(term_id=term_id)
        hits = term2hits.get(term_id, [])
        termid2index[term_id] = i
        if term.term_type == 'C':
            slim_flags.append(0) # C-level
        else:
            slim_flags.append(1)
        term_hits.append(sorted(hits))
        term_ids.append(term.format_id())
        descriptions.append(term.name)
        parents.append(ontology.term2parent[term_id])
        i += 1

    # Second pass inserts term indices in relationships
    for term_id in parents:
        if term_id is not None:
            relationships.append([(termid2index[term_id], 0)])
        else:
            relationships.append([])

    return (['is_a'], slim_flags, term_hits, term_ids, descriptions,
            relationships)


def create_kegg_etd(output_file, gene_info_file, bri_file, gene2kegg_file,
                    org_prefix, tax_id, db_name):
    """
    Write mapping of KEGG terms to NCBI Genes as a SaddleSum ETD (extended term
    database)
    """

    ontology = KEGGOntology(bri_file, org_prefix=org_prefix)
    genes = NCBIGenes_from_gene_info(gene_info_file, tax_id)
    term2hits = _kegg_term2hits(gene2kegg_file, org_prefix, genes)
    data = _kegg_process_namespace(genes, ontology, term2hits)
    data += ([org_prefix, KEGG_LEAF_URL_FMT, KEGG_HIGHER_URL_FMT], )
    with open(output_file, 'wb') as fp:
        write_header(fp, db_name, ['KEGG Pathways'])
        index_gene_info(fp, gene_info_file, tax_id)
        write_namespace(fp, KEGGTERMDB_MAGIC, *data)


def _go_term2hits(gene2go_file, ontology, genes, filter_codes=None):

    if filter_codes is None:
        # IEA filtered by default for compatibility - pass empty
        # list to filter nothing
        filter_codes = set(['IEA'])
    else:
        filter_codes = set(filter_codes)

    term2hits = defaultdict(set)
    term2terms = ontology.all_terms_transitive_closure()
    with open(gene2go_file, 'rb') as gene2go_fp:
        # Process the whole gene2go file
        for line in gene2go_fp:
            if line[0] == '#':
                continue
            flds = line.split('\t')
            gene_id, term_id, evidence, qualifier = flds[1:5]
            gene_id = int(gene_id)

            if qualifier != 'NOT' and evidence not in filter_codes \
                   and gene_id in genes.gene_id2index:
                i = genes.gene_id2index[gene_id]
                if term_id in term2terms:
                    for term_id2 in term2terms[term_id]:
                        term2hits[term_id2].add(i)
    return _filter_term2hits(term2hits)


def _go_process_namespace(genes, ontology, namespace, term2hits):

    termid2index = {}
    slim_flags = []
    term_hits = []
    term_ids = []
    descriptions = []
    unmapped_rels = []
    relationships = []
    edgetypes = set()

    ns_terms = [term_id for term_id in term2hits \
                if ontology.get_term(term_id=term_id).namespace == namespace]
    all_terms, _ = ontology.transitive_closure(ns_terms)

    # First pass
    i = 0
    for term_id in all_terms:
        term = ontology.get_term(term_id=term_id)
        hits = term2hits.get(term_id, [])
        termid2index[term_id] = i
        slim_flags.append(0)
        term_hits.append(sorted(hits))
        term_ids.append(term.format_id())
        descriptions.append(term.name)
        rel_lst = []
        for edge_type, parent in term.relationships:
            rel_lst.append((parent, edge_type))
            edgetypes.add(edge_type)
        unmapped_rels.append(rel_lst)
        i += 1

    # Second pass inserts term indices in relationships
    edgetypes = sorted(edgetypes)
    edgetypes2index = dict((s, i) for i, s in enumerate(edgetypes))
    for rel_lst in unmapped_rels:
        ix_lst = [(termid2index[term_id], edgetypes2index[edge_type]) \
                  for term_id, edge_type in rel_lst]
        relationships.append(ix_lst)

    return (edgetypes, slim_flags, term_hits, term_ids, descriptions,
            relationships)


def create_go_etd(output_file, gene_info_file, obo_file, gene2go_file,
                        tax_id, db_name, filter_codes=None):
    """
    Write mapping of GO terms to NCBI Genes as a SaddleSum ETD (extended term
    database)
    """

    ontology = OBOntology(obo_file)
    namespaces = set()

    genes = NCBIGenes_from_gene_info(gene_info_file, tax_id)
    term2hits = _go_term2hits(gene2go_file, ontology, genes, filter_codes)

    # Get all namespaces
    for term_id in term2hits:
        term = ontology.get_term(term_id=term_id)
        namespaces.add(term.namespace)
    namespaces = sorted(namespaces)

    with open(output_file, 'wb') as fp:
        write_header(fp, db_name, namespaces)
        index_gene_info(fp, gene_info_file, tax_id)
        for ns in namespaces:
            data = _go_process_namespace(genes, ontology, ns, term2hits)
            data += ([GOTERM_URL_FMT], )
            write_namespace(fp, GOTERMDB_MAGIC, *data)


def create_combined_etd(output_file, gene_info_file, obo_file, gene2go_file,
                        bri_file, gene2kegg_file, org_prefix, tax_id, db_name,
                        filter_codes=None):
    """
    Write mappings of GO and KEGG terms to NCBI Genes as a SaddleSum ETD
    (extended term database)
    """
    namespaces = set()
    genes = NCBIGenes_from_gene_info(gene_info_file, tax_id)

    ontology = OBOntology(obo_file)
    term2hits = _go_term2hits(gene2go_file, ontology, genes, filter_codes)

    # Get all namespaces
    for term_id in term2hits:
        term = ontology.get_term(term_id=term_id)
        namespaces.add(term.namespace)
    namespaces = sorted(namespaces) + ['KEGG Pathways']

    with open(output_file, 'wb') as fp:
        write_header(fp, db_name, namespaces)
        index_gene_info(fp, gene_info_file, tax_id)
        # Gene Ontology
        for ns in namespaces[:-1]:
            data = _go_process_namespace(genes, ontology, ns, term2hits)
            data += ([GOTERM_URL_FMT], )
            write_namespace(fp, GOTERMDB_MAGIC, *data)

        # KEGG
        ontology = KEGGOntology(bri_file, org_prefix=org_prefix)
        term2hits = _kegg_term2hits(gene2kegg_file, org_prefix, genes)
        data = _kegg_process_namespace(genes, ontology, term2hits)
        data += ([org_prefix, KEGG_LEAF_URL_FMT, KEGG_HIGHER_URL_FMT], )
        write_namespace(fp, KEGGTERMDB_MAGIC, *data)


def _write_gmt(gmt_file, genes, ontology, term2hits):
    with open(gmt_file, 'wb') as fp:
        for term_id, hits in term2hits.iteritems():
            term = ontology.get_term(term_id=term_id)
            fp.write('%s\t%s' % (term.format_id(), term.name))
            for entity_index in hits:
                symbol = genes.get_record(index=entity_index).gene_id
                fp.write('\t%s' % symbol)
            fp.write('\n')


def create_kegg_gmt(output_file, gene_info_file, bri_file, gene2kegg_file,
                    org_prefix, tax_id):
    """Create a GMT database from KEGG pathways"""

    ontology = KEGGOntology(bri_file, org_prefix=org_prefix)
    genes = NCBIGenes_from_gene_info(gene_info_file, tax_id)
    term2hits = _kegg_term2hits(gene2kegg_file, org_prefix, genes)
    #HERE MODIFY KEYS
    _write_gmt(output_file, genes, ontology, term2hits)


def create_go_gmt(output_file, gene_info_file, obo_file, gene2go_file,
                  tax_id, namespace=None, filter_codes=None):
    """Create a GMT database from a GO namespace"""

    ontology = OBOntology(obo_file)
    genes = NCBIGenes_from_gene_info(gene_info_file, tax_id)
    term2hits = _go_term2hits(gene2go_file, ontology, genes, filter_codes)
    # Filter namespace
    if namespace is not None:
        for term_id in term2hits.keys():
            term = ontology.get_term(term_id=term_id)
            if term.namespace != namespace:
                term2hits.pop(term_id)
    _write_gmt(output_file, genes, ontology, term2hits)
