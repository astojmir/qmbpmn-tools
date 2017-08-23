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
import time
import urllib
import numpy as np
from .. import validators as vld
from .. import exceptions as exc
from ...common.utils.pickling import save_object
from .display_opts import DisplayOpts
from .network import ITMProbeNetwork
from ...ITMProbe import commands

class InfoPropModel(object):
    """
    A class with routines for obtaining ITM Probe results and displaying it on
    the web
    """

    options = []
    param_legend = "Model Parameters"
    _ranking_attrs = None
    _criteria = None
    _renderings = None

    general_options = [('antisink_map',
                        {},
                        vld.antisink_map_validator,
                        'Excluded nodes'),
                       ]

    @classmethod
    def input_page_name(cls):
        return cls.html_template

    def __init__(self):

        self.query_id = None
        self.warning_msgs = None
        self.itm_path = None
        self.network_file = None
        self.enrich_termdb_names = None
        self.enrich_files = None
        self.display_options = DisplayOpts(list(self._ranking_attrs),
                                           list(self._criteria),
                                           list(self._renderings))
    @staticmethod
    def get_query_id():
        """
        Create a unique query identifier.
        For now just hashes current time.
        """
        hash_val = long(np.uint32(hash(time.time())))
        return '%X' % hash_val

    def run_model(self, cgi_map, network_files, storage_path, saddlesum_path):
        """ Main model running routine """

        # Concatenate antisinks from uploaded file to antisinks from text area
        cgi_map['antisink_map'] += cgi_map.pop('antisink_map2')

        # Load the network
        if 'graph' in cgi_map:
            graph_id = cgi_map['graph']
            if graph_id not in network_files:
                raise exc.ValidationError('graph', graph_id)
        else:
            raise exc.InsufficientArgsError('graph')
        self.network_file = network_files[graph_id]
        net = ITMProbeNetwork(self.network_file, True)

        # Get input arguments
        model_kwargs = self.validate_model_args(cgi_map, net)
        net.G.name = net.network_name
        model_kwargs['G'] = net.G

        # Set stored variables
        self.query_id = self.get_query_id()
        model_kwargs['extra_input_params'] = [('Query ID', self.query_id)]
        self.warning_msgs = net.warning_messages
        self.enrich_termdb_names = net.get_enrich_termdb_names(saddlesum_path)
        self.enrich_files = net.enrich_files
        self.itm_path = os.path.join(storage_path, '%s.itm' % self.query_id)

        # Main run
        model_class = commands.model_classes[self.solution_class]
        model_solution = model_class(**model_kwargs)
        self.set_display_settings(model_solution)

        # Save solution plus settings
        model_solution.save(self.itm_path)
        save_object(self, storage_path, self.query_id)

        # Return the link to the 'true' results page
        url_map = self.display_options.get_layout_url_map(cgi_map,
                                                          self.query_id)
        rendering_url = 'ITMProbe.cgi?view=1&%s' % urllib.urlencode(url_map)
        return rendering_url

    def validate_model_args(self, cgi_map, network):
        """ Validate model options """

        model_kwargs = {}
        for opt in self.general_options + self.options:
            name, default_val, validator, label_text = opt
            label_text = name if label_text is None else label_text

            if validator is not None and name in cgi_map:
                model_kwargs[name] = validator(label_text,
                                               cgi_map[name],
                                               network=network)
            elif default_val is None:
                raise exc.InsufficientArgsError(label_text)
            else:
                model_kwargs[name] = default_val
        return model_kwargs

    def set_display_settings(self, model_solution):
        """ Adjust default display settings based on computed results """
        pass

    def _process_node_table(self, header, body):

        network = ITMProbeNetwork(self.network_file, False)
        network.open_genes()

        # Add links
        header.append('Links')
        for line in body:
            gene_id = network.symbol2gene_id(line[1])
            gene_link = '<a target="gene-window" href="%s">NCBI</a>' % \
              (network.node_url_fmt % {'gene_id': gene_id})
            line.append(gene_link)

    def report_tables(self, layout_args):
        """ Produce report tables for html output"""

        kwargs = dict(show_excluded_nodes=True)
        kwargs.update((k, v) for k, v in layout_args.iteritems() \
                      if k in ('max_rows', 'order_by',
                               'use_participation_ratio', 'cutoff_value'))
        raw_tables = commands.report_tables([self.itm_path], **kwargs)

        # Parameters table
        title, header, body, float_cols = raw_tables[0]
        params_table = {'header': header,
                        'body': body,
                        'col_classes': ['col-param', 'col-paramval'],
                        'title': title,
                        'id': 'input-params',
                        }

        # Summary table
        title, header, body, float_cols = raw_tables[1]
        summary_table = {'header': header,
                         'body': body,
                         'col_classes': ['col-quanity', 'col-val'],
                         'title': title,
                         'id': 'summary-table',
                         }

        # Node table
        title, header, body, float_cols = raw_tables[2]
        self._process_node_table(header, body)
        col_classes = ['col-rank', 'col-node'] + \
                      ['col-score']*(len(float_cols)-1) + ['col-links']
        node_table = {'header': header,
                      'body': body,
                      'col_classes': col_classes,
                      'title': title,
                      'id': 'nodes-table',
                      }

        # Excluded table
        title, header, body, float_cols = raw_tables[3]
        excluded_table = {'header': None,
                          'body': body,
                          'col_classes': None,
                          'title': title,
                          'id': 'excluded-nodes',
                          }

        tables = {'summary_table': summary_table,
                  'node_table': node_table,
                  'params_table': params_table,
                  'excluded_table': excluded_table,
                  }

        return tables


