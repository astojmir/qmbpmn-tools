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
Web interface for absorbing model.
"""

from .models import InfoPropModel
from .. import validators as vld
from .. import exceptions as exc
from .rendering import one_color_rendering
from .rendering import mixed_colors_rendering
from .selection_criteria import SELECTION_BY_MAXIMUM_NODES
from .selection_criteria import SELECTION_BY_VALUE_CUTOFF

class AbsorbingModel(InfoPropModel):
    """
    Implements web interface to AbsorbingAnalysis.
    """

    solution_class = 'absorbing'
    title = 'Absorbing model'
    description = \
                """
                Given absorbing sinks of information, find the nodes most likely
                to send information to them.
                """

    html_value = "absorbing"
    html_text = "Absorbing Model"
    html_template = "absorbing.html"
    param_legend = "Absorbing Model Parameters"
    options = [('sink_nodes', None, vld.protein_list_validator, 'Sinks'),
               ('dfcrit', None, vld.dfcrit_validator, ''),
               ('df', None, vld.df_validator, 'Node Dissipation'),
               ('ap', 1e-02, vld.da_validator, 'Average absorption probability'),
               ]

    _ranking_attrs = [('Total Likelihood', 'total_content', 'total_content')]

    _criteria = [SELECTION_BY_MAXIMUM_NODES,
                 SELECTION_BY_VALUE_CUTOFF,
                 ]

    _renderings = [one_color_rendering('Total Likelihood', 'tct', 'total_content')]
    max_sinks = 6

    def validate_model_args(self, cgi_map, network):
        """
        Validate all model options.
        Also limits the number of sinks.
        """
        model_kwargs = InfoPropModel.validate_model_args(self, cgi_map, network)

        dfcrit = model_kwargs.pop('dfcrit')
        if dfcrit == 'df':
            model_kwargs['ap'] = None
        elif dfcrit == 'ap':
            model_kwargs['df'] = None

        if ('sink_nodes' not in model_kwargs) or \
               (len(model_kwargs['sink_nodes']) == 0):
            raise exc.InsufficientSinks()
        if (len(model_kwargs['sink_nodes']) > self.max_sinks):
            raise exc.TooManyBoundaries('sinks', self.max_sinks)

        return model_kwargs


    def set_display_settings(self, model_solution):

        renderings = self.display_options.renderings
        sink_nodes = model_solution.sink_nodes
        num_sinks = len(sink_nodes)

        if num_sinks > 1:
            if num_sinks < 4:
                _tmp = mixed_colors_rendering('Probablilities (color mixture)',
                                              'mix', None)
                renderings.append(_tmp)

            for i, snk in enumerate(sink_nodes):
                text = 'Absorbing probability to %s' % snk
                val = 'dc%d' % i
                vattr = 'datacol%d' % i
                renderings.append(one_color_rendering(text, val, vattr))
