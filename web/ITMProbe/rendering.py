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
from .display_opts import _selector


def brewer_colormaps(num_colors):
    """Generate a list of (preferred) Brewer colormaps """

    _colormaps = ['Blues', 'Reds', 'Greys', 'Greens', 'Oranges', 'YlGn',
                  'YlGnBu', 'GnBu', 'RdPu', 'PuRd', 'BrBG']
    n = str(num_colors)
    return ('%s%s' % (colormap, n) for colormap in _colormaps)


class RenderingSettings(object):
    """ Processing image rendering options from CGI input."""

    def __init__(self, text, form_value, value_attr,
                 scaling_functions, colormaps, additional_args=None):

        self.text = text
        self.form_value = form_value
        self.value_attr = value_attr
        self.scaling_functions = scaling_functions
        self.colormaps = colormaps
        self.additional_args = additional_args if additional_args else {}

    def master_option_data(self):
        m_opt = {'value': self.form_value,
                 'text': self.text,
                 'sSel': [{'id': 'bins_func',
                           'sOpt': [{'text':t, 'value':v} \
                                    for t,v, _ in self.scaling_functions ]},
                          {'id': 'color_map',
                           'sOpt': [{'text':t, 'value':v} \
                                    for t,v, _ in self.colormaps ]},
                          ],
                 'sProp': []}
        return m_opt


    def _get_cgi_args(self, cgi_map):

        # Scalings
        allowed_scalings = dict((fv, val) for _,fv,val in self.scaling_functions)
        default = (self.scaling_functions[0][2], self.scaling_functions[0][1])
        bins_func, bins_val = vld.find_input_option(cgi_map, 'bins_func', allowed_scalings, default)

        # Colormaps
        allowed_colormaps = dict((fv, val) for _,fv,val in self.colormaps)
        default = (self.colormaps[0][2], self.colormaps[0][1])
        cmap, cmap_val = vld.find_input_option(cgi_map, 'color_map', allowed_colormaps, default)

        return  bins_func, bins_val, cmap, cmap_val

    def get_url_args(self, cgi_map, url_map):

        bins_func, bins_val, cmap, cmap_val = self._get_cgi_args(cgi_map)
        url_map['value_attr'] = self.form_value
        url_map['bins_func'] = bins_val
        url_map['color_map'] = cmap_val

    def validate(self, cgi_map, args_map):

        bins_func, _, cmap, _ = self._get_cgi_args(cgi_map)
        args_map['value_cols'] = self.value_attr
        args_map['colormap'] = cmap
        args_map['bins_func'] = bins_func
        args_map['mixed_colors'] = (cmap is None)
        args_map.update(self.additional_args)




def one_color_rendering(text, form_value, value_attr):
    """ Standard rendering option with a single color """

    scaling_functions = [('Logarithmic', 'log2', 'log_upper'),
                         ('Linear', 'none', 'linear')]
    colormaps = [(M, M.lower(), M) for M in brewer_colormaps(8)]

    return RenderingSettings(text, form_value, value_attr, scaling_functions,
                             colormaps)

def mixed_colors_rendering(text, form_value, value_attr):
    """ Standard rendering option with a mixed colors """

    scaling_functions = [('Sqrt', 'sqrt', 'sqrt'),
                         ('Linear', 'none', 'linear')]
    colormaps = [('CMY mixed', 'cmy_mixed', None)]

    return RenderingSettings(text, form_value, value_attr, scaling_functions,
                             colormaps)
