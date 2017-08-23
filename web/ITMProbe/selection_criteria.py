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

""" Selection criteria for ITM layout"""
from .display_opts import _selector


class SelectionSettings(object):
    def __init__(self, text, form_value, use_participation_ratio,
                 show_value_cutoff):

        self.text = text
        self.form_value = form_value
        self.use_participation_ratio = use_participation_ratio
        self.show_value_cutoff = show_value_cutoff

    def master_option_data(self):
        visibility = 'visible' if self.show_value_cutoff else 'hidden'
        m_opt = {'value': self.form_value,
                 'text': self.text,
                 'sSel': [],
                 'sProp': [{'selector': _selector('value_cutoff'),
                            'property': 'visibility',
                            'value': visibility,
                            'style': '1'},
                           {'selector': _selector('display_panel',
                                                  'value_cutoff',
                                                  'for',
                                                  'label'),
                            'property': 'visibility',
                            'value': visibility,
                            'style': '1'},
                           ],
                 }
        return m_opt

    def validate(self, cgi_map, args_map, form_properties, form_masters,
                 form_selections):

        args_map['use_participation_ratio'] = self.use_participation_ratio
        form_masters.append(_selector('selection_criterion',
                                      self.form_value,
                                      'value',
                                      'option'))
        if self.show_value_cutoff:
            val = float(cgi_map['value_cutoff'])
            args_map['cutoff_value'] = val
            form_properties.append((_selector('value_cutoff'),
                                    'value', str(val),'0'))
        else:
            args_map['cutoff_value'] = None


SELECTION_BY_PARTICIPATION_RATIO = SelectionSettings('Participation Ratio',
                                                     'pratio', True, False)

SELECTION_BY_MAXIMUM_NODES = SelectionSettings('Maximum Nodes', 'max_nodes',
                                               False, False)

SELECTION_BY_VALUE_CUTOFF = SelectionSettings('Cutoff Value', 'value_cutoff',
                                              False, True)
