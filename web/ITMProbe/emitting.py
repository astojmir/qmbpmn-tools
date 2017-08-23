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
Web interface for emitting model.
"""

from .models import InfoPropModel
from .. import validators as vld
from .. import exceptions as exc
from .rendering import one_color_rendering
from .rendering import mixed_colors_rendering
from .selection_criteria import SELECTION_BY_PARTICIPATION_RATIO
from .selection_criteria import SELECTION_BY_MAXIMUM_NODES
from .selection_criteria import SELECTION_BY_VALUE_CUTOFF


class EmittingModel(InfoPropModel):
    """
    Implements web interface to EmittingAnalysis.
    """
    solution_class = 'emitting'
    title = 'Emitting model'
    description = \
    """
    Given emitting sources, find the nodes most visited by the flow.
    """

    html_value = "emitting"
    html_text = "Emitting Model"
    html_template = "emitting.html"
    param_legend = "Emitting Model Parameters"
    options = [('source_nodes', None, vld.protein_list_validator, 'Sources'),
               ('dfcrit', None, vld.dfcrit_validator, ''),
               ('da', 5.0, vld.da_validator, 'Path-length deviation (absolute)'),
               ('df', None, vld.df_validator, 'Node Dissipation'),
               ]

    _ranking_attrs = [('Total Visits', 'tct', 'total_content'),
                      ('Interference', 'ifr', 'interference'),
                      ]

    _criteria = [SELECTION_BY_PARTICIPATION_RATIO,
                 SELECTION_BY_MAXIMUM_NODES,
                 SELECTION_BY_VALUE_CUTOFF]

    _renderings = [one_color_rendering('Total Visits', 'tct', 'total_content'),
                   ]
    max_sources = 6

    def validate_model_args(self, cgi_map, network):
        """
        Validate all model options.
        Also limits the number of sources.
        """
        model_kwargs = InfoPropModel.validate_model_args(self, cgi_map, network)

        dfcrit = model_kwargs.pop('dfcrit')
        if dfcrit == 'df':
            model_kwargs['da'] = None
        elif dfcrit == 'da':
            model_kwargs['df'] = None

        if ('source_nodes' not in model_kwargs) or \
               (len(model_kwargs['source_nodes']) == 0):
            raise exc.InsufficientSources()
        if (len(model_kwargs['source_nodes']) > self.max_sources):
            raise exc.TooManyBoundaries('sources', self.max_sources)

        return model_kwargs

    def set_display_settings(self, model_solution):

        renderings = self.display_options.renderings
        source_nodes = model_solution.source_nodes
        num_sources = len(source_nodes)

        if num_sources > 1:
            _tmp = one_color_rendering('Interference', 'ifr', 'interference')
            renderings.append(_tmp)

            if num_sources < 4:
                _tmp = mixed_colors_rendering('Intensities (color mixture)',
                                              'mix', None)
                renderings.append(_tmp)

            for i, src in enumerate(source_nodes):
                text = 'Visits from %s' % src
                val = 'dc%d' % i
                vattr = 'datacol%d' % i
                renderings.append(one_color_rendering(text, val, vattr))


