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
from collections import defaultdict
from urlparse import urljoin
from urllib import urlencode
from ...common.utils.jinjaenv import get_jinja_env


DETAILS_FMT = '<a href="%s?view=c&%s" target="cvterm-scores">%s</a>'
ID_FMT = '<a href="%s" target="_blank">%s</a>'

def _format_term_link(site_url, query_id, term_id, item):
    dfmt = DETAILS_FMT % (urljoin(site_url, 'enrich.cgi'),
                          urlencode({'query_id': query_id,
                                     'termid': term_id}),
                          item)
    return dfmt


def saddlesum_html_results(conf, query_id, summary_body, warning_msgs,
                           unknown_ids_txt, namespaces):
    """
    Process saddlesum output and return it as HTML page.
    """

    site_url = urljoin(conf.site_url,conf.enrich_htdocs_suffix)

    if not len(namespaces):
        image_tag = None
    else:
        image_url = 'enrich.cgi?view=b&%s' % urlencode({'query_id': query_id})
        image_abs_url = urljoin(site_url, image_url)
        image_tag = '<embed src="%s" type="image/svg+xml" ' \
                    'style="width:100%%;height:100%%"/>' % image_abs_url

    ns_headings = [(ns, ns.replace('_', ' ').title()) for ns, _ in namespaces]
    input_summary = {'header': [],
                 'body': summary_body,
                 'col_classes': ['summary_key', 'summary_val'],
                 'warning_msgs': [row[0] for row in warning_msgs],
                 'unknown_ids_txt': ' '.join(row[0] for row in unknown_ids_txt),
                 }

    bodies = {}
    for ns, data in namespaces:
        bodies[ns] = []
        for term_id, name, num_hits, score, Evalue, term_url in data:
            row = [ID_FMT % (term_url, term_id),
                   name,
                   _format_term_link(site_url, query_id, term_id, num_hits),
                   _format_term_link(site_url, query_id, term_id, score),
                   _format_term_link(site_url, query_id, term_id, Evalue)]
            bodies[ns].append(row)

    tables = dict( (ns, {'header': ['Term ID', 'Name', 'Associations',
                                    'Score', 'E-value'] ,
                         'body': bodies[ns],
                         'col_classes': ['col-termid', 'col-node',
                                         'col-assoc', 'col-score2',
                                         'col-score2'],
                         }) for ns in bodies )

    jinja_env =  get_jinja_env(conf)
    tmpl = jinja_env.get_template('enrich/cvterm_results.html')
    return tmpl.render(conf=conf,
                       img_tag=image_tag,
                       category_titles=ns_headings,
                       input_summary=input_summary,
                       tables=tables)



def saddlesum_html_term_scores(conf, summary_body, entities):
    """
    Process saddlesum term scores output and return it as HTML page.
    """

    link_fmt = '<a href="%s" target="ncbi-gene-view">NCBI</a>'
    input_summary = {'header': [],
                     'body': summary_body,
                     'col_classes': ['summary_key', 'summary_val'],
                     }

    # Determine how many nodes to expose by computing participation ratio
    scores = [float(r[3]) if r[3] != 'None' else 0.0 for r in entities]
    total_score = sum(scores)
    participation_ratio = total_score**2 / sum(S**2 for S in scores)
    num_top_nodes = min(int(participation_ratio + 0.5), 30)

    for r in entities:
        r[-1] = link_fmt % r[-1]

    header = ['Rank', 'Identifier', 'Description', 'Score', 'Links']
    col_classes = ['col-rank', 'col-termid', 'col-node', 'col-score2',
                   'col-links']
    top_table = {'header': header,
                 'body': entities[:num_top_nodes],
                 'col_classes': col_classes,
                 }
    other_table = {'header': header,
                   'body': entities[num_top_nodes:],
                   'col_classes': col_classes,
                   }
    tables = {'summary': input_summary,
              'top_scores': top_table,
              'other_scores': other_table,
              }
    jinja_env =  get_jinja_env(conf)
    tmpl = jinja_env.get_template('enrich/cvterm_scores.html')
    return tmpl.render(conf=conf, tables=tables)




