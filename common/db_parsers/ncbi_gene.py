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
Routines for handling NCBI Gene database.
"""

import zlib
import contextlib
from collections import defaultdict
import numpy as np
from ..utils.filesys import write_string_list
from ..utils.filesys import read_string_list

NCBIGENE_URL_FMT = "http://www.ncbi.nlm.nih.gov/sites/entrez?db=gene" \
                   "&cmd=Retrieve&dopt=Graphics&list_uids=%ld"
NCBIGENE_MAGIC = 1200900292  # uint32(crc32('qmbpmn-tools-NCBIGENE'))

def _file_crc32(filename):
    # Compute CRC32 checksum of gene_info_file
    checksum = 0
    with open(filename, 'rb') as fp:
        for line in fp:
            checksum = zlib.crc32(line, checksum)
    return checksum


def _parse_gene_info(gene_info_file, tax_id):

    gene_ids = []
    offsets = []
    symbols = []
    synonyms = []
    descriptions = []
    gene_types = []
    bytecount = 0
    tax_id_ = str(tax_id)

    # Compute CRC32 checksum of gene_info_file
    gene_info_checksum = _file_crc32(gene_info_file)

    # Parse the block for the given tax_id
    with open(gene_info_file, 'rb') as fp:
        species_block = False
        for line in fp:
            bytecount += len(line)
            if line[0] == '#':
                continue
            flds = line.strip().split('\t')
            if not species_block:
                if flds[0] == tax_id_:
                    species_block = True
                    offsets.append(bytecount - len(line))
                else:
                    continue
            if flds[0] != tax_id_:
                break
            gene_ids.append(int(flds[1]))
            offsets.append(bytecount)
            symbols.append(flds[2])
            locus_tag = [flds[3]] if flds[3] != '-' else []
            aliases = flds[4].split('|') if flds[4] != '-' else []
            synonyms.append(locus_tag + aliases)
            gene_types.append(flds[9])
            desc1 = flds[8] if flds[8] != '-' else ""
            descriptions.append(desc1)

    # Ensure that the mapping symbols and gene_ids both give 1-1 mappings -
    # sometimes a primary symbol does map to two different genes (gene_ids).
    # In that case, we push the conflicting symbols to synonyms (they will be
    # dealt with under Case2 below) and use gene_id (in string form) as the
    # primary symbol.

    smb2gid = defaultdict(list)
    for smb, gid in zip(symbols, gene_ids):
        smb2gid[smb].append(gid)

    for i, smb in enumerate(symbols):
        if len(smb2gid[smb]) > 1:
            symbols[i] = str(gene_ids[i])
            synonyms[i].insert(0, smb)

    assert (len(gene_ids) == len(set(gene_ids)))
    assert (len(gene_ids) == len(set(symbols)))

    # Now process aliases
    alias_map = defaultdict(set)
    for smb, syn_lst in zip(symbols, synonyms):
        alias_map[smb].add(smb)
        for syn in syn_lst:
            alias_map[syn].add(smb)

    # Identify and resolve all conflicts between identifiers
    # * Conflict: one identifier maps to multiple objects, either as a
    # standard name or a synonym.
    # * Resolution: 1. standard name takes precedence (other ignored)
    #               2. if same id is a synonym to more than one protein,
    #                   ignore it in both cases.
    # Removed ids go into the conflicts map

    symbol2aliases = dict((smb, []) for smb in symbols)
    conflict1 = defaultdict(set)
    conflict2 = defaultdict(set)

    for syn, smb_set in alias_map.iteritems():
        if len(smb_set) > 1:
            if syn in symbol2aliases:  # Case 1
                smb_set.discard(syn)
                conflict1[syn].update(smb_set)
            else:  # Case 2
                conflict2[syn].update(smb_set)
        else:  # len(smb_set) == 1
            smb = smb_set.pop()
            if smb != syn:
                symbol2aliases[smb].append(syn)

    return (gene_info_file,
            gene_info_checksum,
            tax_id,
            gene_ids,
            offsets,
            symbols,
            symbol2aliases,
            descriptions,
            conflict1,
            conflict2)


def _write_index_1200900292(fp,
                            gene_info_file,
                            gene_info_checksum,
                            tax_id,
                            gene_ids,
                            offsets,
                            symbols,
                            symbol2aliases,
                            descriptions,
                            conflict1,
                            conflict2):

    # *** Index structure ***

    # char start_separator           - 'NCBIGENE'
    # uint32 version_magic           - changes for each different version
    # uint32 metadata_buflen
    # char metadata[metadata_buflen] - gene_info_file, NCBIGENE_URL_FMT
    # uint32 gene_info_checksum      - CRC32 checksum of gene_info_file
    # uint32 tax_id                  - NCBI Taxonomy ID

    # uint32 N
    # uint32 gene_ids[N]             - assumes every NCBI Gene ID is uint32
    # uint32 offsets[N+1]            - offsets into gene_info_file
    # uint32 symbols_counts[N]       - counts of symbol lists for each gene
    # uint32 symbols_buflen
    # char symbols_buf[symbols_len]  - N lists of symbols. Each symbol is
    #                                  terminated by '\0'
    #                                  Each list contains one primary
    #                                  identifier and 0 or more synonyms.
    # uint32 desc1_buflen
    # char desc1[desc1_buflen]       - gene descriptions

    # uint32 num_conf1               - number of conflicts (type1)
    # uint32 conf1_counts[num_conf1] - counts of conflict lists (type 1)
    # uint32 conf1_buflen
    # char conf1_buf[conf1_buflen]   - A list of conflict lists (of type 1).
    #                                  Each symbol terminated by '\0'.
    #                                  The first item in each list conflicts
    #                                  with all the others.

    # uint32 num_conf2               - number of conflicts (type2)
    # uint32 conf2_counts[num_conf2] - counts of conflict lists (type 2)
    # uint32 conf2_buflen
    # char conf2_buf[conf2_buflen]   - A list of conflict lists (of type 2).
    #                                  Each symbol terminated by '\0'.
    #                                  The first item in each list conflicts
    #                                  with all the others.

    metadata = [gene_info_file, NCBIGENE_URL_FMT]

    fp.write('NCBIGENE')
    fp.write(np.array([NCBIGENE_MAGIC], dtype='<u4'))
    write_string_list(fp, metadata, False)
    fp.write(np.array([gene_info_checksum], dtype='<u4'))
    fp.write(np.array([tax_id], dtype='<u4'))
    fp.write(np.array([len(gene_ids)], dtype='<u4'))
    fp.write(np.array(gene_ids, dtype='<u4'))
    fp.write(np.array(offsets, dtype='<u4'))

    counts = [1 + len(symbol2aliases[smb]) for smb in symbols]
    fp.write(np.array([counts], dtype='<u4'))
    str_lst = [s for smb in symbols for s in [smb] + symbol2aliases[smb]]
    write_string_list(fp, str_lst, False)

    write_string_list(fp, descriptions, False)

    counts = [1 + len(conflict1[k]) for k in conflict1]
    fp.write(np.array([len(conflict1)], dtype='<u4'))
    fp.write(np.array([counts], dtype='<u4'))
    str_lst = [s for k, v in conflict1.iteritems() for s in [k] + list(v)]
    write_string_list(fp, str_lst, False)

    counts = [1 + len(conflict2[k]) for k in conflict2]
    fp.write(np.array([len(conflict2)], dtype='<u4'))
    fp.write(np.array([counts], dtype='<u4'))
    str_lst = [s for k, v in conflict2.iteritems() for s in [k] + list(v)]
    write_string_list(fp, str_lst, False)


def _read_index_1200900292(fp):

    header = fp.read(8)
    magic = int(np.frombuffer(fp.read(4), '<u4')[0])

    if header != 'NCBIGENE' or magic != NCBIGENE_MAGIC:
        raise RuntimeError('Invalid format for gene_info index.')

    metadata = read_string_list(fp, False)
    gene_info_file, object_url_fmt = metadata
    gene_info_checksum = int(np.frombuffer(fp.read(4), '<u4')[0])
    tax_id = int(np.frombuffer(fp.read(4), '<u4')[0])
    N = int(np.frombuffer(fp.read(4), '<u4')[0])
    gene_ids = map(int, np.frombuffer(fp.read(4*N), '<u4'))
    offsets = map(int, np.frombuffer(fp.read(4*(N+1)), '<u4'))

    symbols = []
    symbol2aliases = {}
    counts = map(int, np.frombuffer(fp.read(4*N), '<u4'))
    symb_list = read_string_list(fp, False)
    k = 0
    for i in xrange(N):
        smb = symb_list[k]
        symbols.append(smb)
        symbol2aliases[smb] = symb_list[k+1:k+counts[i]]
        k += counts[i]

    descriptions = read_string_list(fp, False)

    conflict1 = {}
    N = int(np.frombuffer(fp.read(4), '<u4')[0])
    if N > 0:
        counts = map(int, np.frombuffer(fp.read(4*N), '<u4'))
        symb_list = read_string_list(fp, False)
        k = 0
        for i in xrange(N):
            smb = symb_list[k]
            conflict1[smb] = set(symb_list[k+1:k+counts[i]])
            k += counts[i]

    conflict2 = {}
    N = int(np.frombuffer(fp.read(4), '<u4')[0])
    if N > 0:
        counts = map(int, np.frombuffer(fp.read(4*N), '<u4'))
        symb_list = read_string_list(fp, False)
        k = 0
        for i in xrange(N):
            smb = symb_list[k]
            conflict2[smb] = set(symb_list[k+1:k+counts[i]])
            k += counts[i]

    return (gene_info_file,
            gene_info_checksum,
            tax_id,
            gene_ids,
            offsets,
            symbols,
            symbol2aliases,
            descriptions,
            conflict1,
            conflict2)


class NCBIGeneRecord(object):
    """Container class for gene records."""

    link_fmt = '<a href="%s" target="ncbi-gene-view">NCBI</a>'

    def __init__(self, symbol, gene_id, description, **kwargs):

        self.symbol = symbol
        self.gene_id = gene_id
        self.description = description
        self.url_fmt = NCBIGENE_URL_FMT
        self.__dict__.update(kwargs)

    def format_id(self):
        """Format gene id for output."""

        return self.symbol

    def format_desc(self):
        """Format gene description for output."""

        return self.description

    def format_links(self):
        """
        Return an html tag with links to external resources about the gene.
        """
        url = self.url_fmt % self.gene_id
        return self.link_fmt % url


class NCBIGenes(object):
    """
    Handles NCBI Genes.
    """

    # Warning types and messages
    UNKNOWN_ID = 0
    CONFLICT_1 = 1
    CONFLICT_2 = 2
    DUPLICATE_ID = 3

    WARNING_FMTS = ['Term database does not contain identifier %(id)s'
                    ' - IGNORED.',
                    'Identifier %(id)s is also used for %(aliases)s.',
                    'Identifier %(id)s is an alias for %(aliases)s'
                    ' - IGNORED.',
                    'Duplicate weight for %(id)s (original id %(aliases)s)'
                    ' - additional instance IGNORED.'
                    ]

    gene_info_fields = ['tax_id', 'gene_id', 'symbol', 'locus_tag', 'synonyms',
                        'dbXrefs', 'chromosome', 'map_location', 'description',
                        'type_of_gene', 'symbol_from_nomenclature_authority',
                        'full_name_from_nomenclature_authority',
                        'nomenclature_status', 'other_designations',
                        'modification_date']

    def __init__(self, gene_info_file, gene_info_checksum, tax_id, gene_ids,
                 offsets, symbols, symbol2aliases, descriptions, conflict1,
                 conflict2):

        self.gene_info_fp = None
        self.gene_info_file = gene_info_file
        self.gene_info_checksum = gene_info_checksum
        self.tax_id = tax_id

        self.num_objects = len(gene_ids)
        self.gene_ids = gene_ids
        self.offsets = offsets
        self.symbols = symbols
        self.symbol2aliases = symbol2aliases
        self.descriptions = descriptions

        self.gene_id2index = dict((g, i) for i, g in enumerate(gene_ids))
        self.alias2index = dict((smb, i) for i, smb in enumerate(symbols))
        self.alias2index.update((alias, i) for i, smb in enumerate(symbols) \
                                           for alias in symbol2aliases[smb])

        self.conflicts = dict((smb, (self.CONFLICT_1, sorted(smb_set))) \
                              for smb, smb_set in conflict1.iteritems())
        self.conflicts.update((smb, (self.CONFLICT_2, sorted(smb_set))) \
                              for smb, smb_set in conflict2.iteritems())

    def open_gene_info(self):
        """
        Open gene_info_file to have access to full records.
        """
        if self.gene_info_fp is None:
            # Verify CRC32 sum
            if self.gene_info_checksum != _file_crc32(self.gene_info_file):
                raise RuntimeError('gene_info CRC32 sum does not agree')
            self.gene_info_fp = open(self.gene_info_file, 'rb')

    def close_gene_info(self):
        """
        Close gene_info_file if open.
        """
        if self.gene_info_fp is not None:
            self.gene_info_fp.close()
            self.gene_info_fp = None

    def map_symbols(self, symbols):
        """
        For each symbol in symbols (an iterable), returns the pair
        (i, warnings) where i is an index corresponding to the gene represented
        by symbol and warnings is either None (everything OK) or a triple
        (symbol, warning_type, data) in the case of ambiguous or repeated
        symbol. A symbol can be either an integer (NCBI Gene Id) or a
        recognised symbol.
        """

        res = []
        used_indices = {}
        for smb in symbols:
            warn = None
            try:
                gene_id = int(smb)
                i = self.gene_id2index.get(gene_id, None)
            except ValueError:
                i = self.alias2index.get(smb, None)
                if i is None:
                    smb1 = smb.upper()
                    if smb1 in self.alias2index:
                        i = self.alias2index[smb1]
                        smb = smb1

            if i is None:
                # It is either a conflict or an unknown symbol
                wtype, data = self.conflicts.get(smb, (self.UNKNOWN_ID, None))
                warn = (smb, wtype, {'aliases': data})
            elif i in used_indices:
                # Warn that we've seen this index before.
                warn = (smb, self.DUPLICATE_ID, {'aliases': [used_indices[i]]})
            else:
                # Check if there are more conflicts with this symbol
                if smb in self.conflicts:
                    wtype, data = self.conflicts[smb]
                    warn = (smb, wtype, {'aliases': data})
                used_indices[i] = smb
            res.append((i, warn))
        return res, np.array(sorted(used_indices.iterkeys()), dtype='uint32')

    def map_symbols_to_gene_ids(self, symbols):
        """
        Same as map_symbols except that gene_ids are returned instead of local
        indices.
        """
        res0, used_indices = self.map_symbols(symbols)
        res1 = [(self.gene_ids[i] if i is not None else None, warn) \
                for (i, warn) in res0]
        used_ids = [self.gene_ids[i] for i in used_indices]
        return res1, used_ids

    def get_record(self, index=None, gene_id=None, symbol=None):
        """
        Retrieves a full record from the gene_info database. The record is
        specified using either an internal index (index), gene_id or a gene
        symbol (including valid synonyms) and returned as a dictionary. Exactly
        one of the ways must be used. Raises KeyError if the record cannot be
        found.
        """

        assert (2 == (index is None) + (gene_id is None) + (symbol is None)), \
               "Exactly one of index, gene_id or symbol must be specified."

        if gene_id is not None:
            gene_id = int(gene_id)
            index = self.gene_id2index[gene_id]
        elif symbol is not None:
            index = self.alias2index[symbol]

        gene_id = self.gene_ids[index]
        symbol = self.symbols[index]
        description = self.descriptions[index]

        if self.gene_info_fp is not None:

            self.gene_info_fp.seek(self.offsets[index])
            nb = self.offsets[index+1]-self.offsets[index]
            line = self.gene_info_fp.read(nb)
            flds = line.strip().split('\t')

            # Convert '-' into None for empty fields
            flds = map(lambda s: None if s == '-' else s, flds)

            # Process individual fields
            flds[0] = int(flds[0])
            flds[1] = int(flds[1])
            if flds[4]:
                flds[4] = flds[4].split('|')

            record = dict(r for r in zip(self.gene_info_fields, flds) \
                          if r[0] not in ['symbol', 'gene_id', 'description'])
        else:
            record = {}

        return NCBIGeneRecord(symbol, gene_id, description, **record)

    def format_id_list(self, id_list):

        if id_list:
            # Format list of ids
            N = len(id_list)
            if N == 1:
                s = id_list[0]
            else:
                seps = [', '] * N
                seps[-1] = ''
                seps[-2] = ' and '
                s = ''.join(['%s%s' % word for word in zip(id_list, seps)])
        else:
            s = ''
        return s

    def warning_msgs(self, warnings, exclude_types=None, warning_fmts=None):
        """
        Returns warning messages for sumbitted warning triples, skipping those
        having warning_type in exclude_types.
        """

        messages = []
        if exclude_types is None:
            exclude_types = set([self.UNKNOWN_ID])
        if warning_fmts is None:
            warning_fmts = self.WARNING_FMTS
        for node, warning_type, data in warnings:
            if warning_type in exclude_types:
                continue
            if 'aliases' in data:
                data['aliases'] = self.format_id_list(data['aliases'])
            data['id'] = node
            msg = warning_fmts[warning_type] % data
            messages.append(msg)
        return messages


def index_gene_info(fp_out, gene_info_file, tax_id):
    """
    Creates an index into the NCBI Gene tab separated file.
    Only the genes from the species with tax_id are indexed.
    The file is assumed to be sorted on tax_id (or at least that all
    tax_ids are in one block.
    Index is output in binary format into fp_out.
    """

    data = _parse_gene_info(gene_info_file, tax_id)
    _write_index_1200900292(fp_out, *data)


def NCBIGenes_from_index(fp):
    """
    Context manager returning NCBIGenes instance using precomputed index.
    """
    data = _read_index_1200900292(fp)
    return NCBIGenes(*data)


def NCBIGenes_from_gene_info(gene_info_file, tax_id):
    """
    Context manager returning NCBIGenes obtained by parsing gene_info
    directly.
    """
    data = _parse_gene_info(gene_info_file, tax_id)
    return NCBIGenes(*data)
