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

from .. import validators as vld
from .. import exceptions as exc
from .models import InfoPropModel
from .emitting import EmittingModel


class NormChannelModel(EmittingModel):
    solution_class = 'normalized-channel'
    title = 'Channel model'
    description =\
                """
                Find the most likely paths between given sources and sinks.
                """
    html_value = "channel"
    html_text = "Channel Model"
    html_template = "channel.html"
    param_legend = "Channel Model Parameters"

    options = [('source_nodes', None, vld.protein_list_validator, 'Sources'),
               ('sink_nodes', None, vld.protein_list_validator, 'Sinks'),
               ('dfcrit', None, vld.dfcrit_validator, ''),
               ('df', 0.15, vld.df_validator, 'Node Dissipation'),
               ('da', 2.0, vld.da_validator, 'Path-length deviation (absolute)'),
               ('dr', 0.3, vld.da_validator, 'Path-length deviation (relative)'),
               ]

    max_sources = 6
    max_sinks = 6

    def validate_model_args(self, cgi_map, network):
        """
        Validate all model options.
        """

        model_kwargs = InfoPropModel.validate_model_args(self, cgi_map, network)

        dfcrit = model_kwargs.pop('dfcrit')
        if dfcrit == 'df':
            model_kwargs['da'] = None
            model_kwargs['dr'] = None
        elif dfcrit == 'da':
            model_kwargs['df'] = None
            model_kwargs['dr'] = None
        elif dfcrit == 'dr':
            model_kwargs['df'] = None
            model_kwargs['da'] = None

        num_sources = len(model_kwargs['source_nodes'])
        num_sinks = len(model_kwargs['sink_nodes'] )
        if num_sources == 0:
            raise exc.InsufficientSources()
        if num_sinks == 0:
            raise exc.InsufficientSinks()
        if (num_sources > self.max_sources):
            raise exc.TooManyBoundaries('sources', self.max_sources)
        if (num_sinks > self.max_sinks):
            raise exc.TooManyBoundaries('sinks', self.max_sinks)

        return model_kwargs
