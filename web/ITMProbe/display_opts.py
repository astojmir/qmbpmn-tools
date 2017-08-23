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

import urllib
from .. import validators as vld
from ...common.graphics import image_processors as imp

_PROPERTY_TAGS = ['selector', 'property', 'value', 'style']

def _selector(nodeId, attrValue=None, attrName=None, tag=None):
    S = {'nodeId': nodeId}
    if attrValue:
        S.update({'attrValue': attrValue,
                  'attrName': attrName,
                  'tag': tag,
                  })
    return S


DEFAULT_MAX_NODES = 40
DEFAULT_NEATO_SEED = 54321
DEFAULT_VALUE_CUTOFF = 0.05


class DisplayOpts(object):

    image_processors = imp.IMAGE_PROCESSORS

    def __init__(self, ranking_attrs, criteria, renderings):

        self.ranking_attrs = ranking_attrs
        self.criteria = criteria
        self.renderings = renderings

        self.form_properties = []
        self.form_masters = []
        self.form_selections = []

    def _get_ranking_attr(self, cgi_map, layout_args_map):

        allowed = dict((r[1], r[2]) for r in self.ranking_attrs)
        default = (self.ranking_attrs[0][2], self.ranking_attrs[0][1])
        val, form_val = vld.find_input_option(cgi_map, 'ranking_attr', allowed, default)
        self.form_masters.append(_selector('ranking_attr', form_val, 'value', 'option'))

        layout_args_map['order_by'] = val
        return {'ranking_attr': form_val}

    def _get_criterion(self, cgi_map, layout_args_map):

        allowed = dict((R.form_value, R) for R in self.criteria)
        default = (self.criteria[0], self.criteria[0].form_value)
        crit, form_val = vld.find_input_option(cgi_map, 'selection_criterion', allowed, default)
        crit.validate(cgi_map, layout_args_map, self.form_properties, self.form_masters,
                      self.form_selections)

        ret_vals = {}
        ret_vals['value_cutoff'] = cgi_map.get('value_cutoff', str(DEFAULT_VALUE_CUTOFF))
        ret_vals['selection_criterion'] = form_val
        return ret_vals

    def _get_max_nodes(self, cgi_map, layout_args_map):

        if 'max_nodes' not in cgi_map:
            val = DEFAULT_MAX_NODES
        else:
            val = vld.int_validator('max_nodes', cgi_map['max_nodes'], 1, 200)
        self.form_properties.append((_selector('max_nodes'),'value',str(val),'0'))

        layout_args_map['max_rows'] = val
        return {'max_nodes': str(val)}

    def _get_neato_seed(self, cgi_map, layout_args_map):

        if 'neato_seed' not in cgi_map:
            val = DEFAULT_NEATO_SEED
        else:
            val = vld.int_validator('neato_seed', cgi_map['neato_seed'], 0, 2**32-1)
        self.form_properties.append((_selector('neato_seed'), 'value', str(val), '0'))

        layout_args_map['neato_seed'] = val
        return {'neato_seed': str(val)}

    def _find_rendering(self, cgi_map):

        allowed = dict((r.form_value, r) for r in self.renderings)
        default = (self.renderings[0], self.renderings[0].form_value)
        rndr, _ = vld.find_input_option(cgi_map, 'value_attr', allowed, default)
        return rndr

    def _get_rendering(self, cgi_map, rendering_args_map):

        rndr = self._find_rendering(cgi_map)
        rndr.validate(cgi_map, rendering_args_map)

    def _find_image_proc(self, cgi_map):

        default = (imp.IMAGE_PROCESSORS[0], imp.IMAGE_PROCESSORS[0].name)
        img_proc, _ = vld.find_input_option(cgi_map, 'image_format',
                                            imp.IMG_PROC_MAP, default)
        return img_proc

    def _get_image_format(self, cgi_map, rendering_args_map):

        img_proc = self._find_image_proc(cgi_map)
        rendering_args_map['neato_options'] = img_proc.neato_option

    def validate_display_args(self, cgi_map):

        # These will be filled by validating subroutines
        self.form_properties = []
        self.form_masters = []
        self.form_selections = []

        # Validate layout arguments and construct layout_args_map
        layout_args_map = {}
        self._get_ranking_attr(cgi_map, layout_args_map)
        self._get_criterion(cgi_map, layout_args_map)
        self._get_max_nodes(cgi_map, layout_args_map)
        self._get_neato_seed(cgi_map, layout_args_map)

        # Update rendering form settings
        tmp_map = {}
        rndr = self._find_rendering(cgi_map)
        rndr.get_url_args(cgi_map, tmp_map)
        self.form_masters.append(_selector('value_attr', tmp_map['value_attr'],
                                           'value', 'option'))
        self.form_selections.append(_selector('bins_func', tmp_map['bins_func'],
                                              'value', 'option'))
        self.form_selections.append(_selector('color_map', tmp_map['color_map'],
                                              'value', 'option'))
        img_proc = self._find_image_proc(cgi_map)
        self.form_selections.append(_selector('image_format', img_proc.name,
                                              'value', 'option'))

        return layout_args_map

    def validate_rendering_args(self, cgi_map):

        rendering_args_map = {}
        args2 = (cgi_map, rendering_args_map)

        self._get_rendering(*args2)
        self._get_image_format(*args2)

        return rendering_args_map


    def get_image_url_map(self, cgi_map, query_id, layout_id):
        """
        Constructs image url map and also obtaines some form settings.
        """

        url_map = {'query_id': query_id,
                   'layout_id': layout_id}

        rndr = self._find_rendering(cgi_map)
        rndr.get_url_args(cgi_map, url_map)

        img_proc = self._find_image_proc(cgi_map)
        url_map['image_format'] = img_proc.name
        return url_map

    def get_layout_url_map(self, cgi_map, query_id):

        url_map = self.get_image_url_map(cgi_map, query_id, 'NONE')
        del url_map['layout_id']

        url_map.update(self._get_ranking_attr(cgi_map, {}))
        url_map.update(self._get_criterion(cgi_map, {}))
        url_map.update(self._get_max_nodes(cgi_map, {}))
        url_map.update(self._get_neato_seed(cgi_map, {}))

        return url_map


    def image_spec(self, cgi_map, query_id, layout_id):

        url_map = self.get_image_url_map(cgi_map, query_id, layout_id)
        url_map.update(self._get_ranking_attr(cgi_map, {}))
        url_map.update(self._get_criterion(cgi_map, {}))
        url_map.update(self._get_max_nodes(cgi_map, {}))
        url_map.update(self._get_neato_seed(cgi_map, {}))

        img_proc = self._find_image_proc(cgi_map)
        image_url = 'ITMProbe.cgi?view=2&%s' % urllib.urlencode(url_map)
        return img_proc.html(image_url)


    def master_select_data(self):

        master_data = {'ranking_attr': {'mOpt': [{'text':r[0], 'value':r[1], 'sSel':[], 'sProp':[]} \
                                                 for r in self.ranking_attrs ]},
                       'selection_criterion': {'mOpt': [r.master_option_data() for r in self.criteria ]},
                       'value_attr': {'mOpt': [r.master_option_data() for r in self.renderings ]}
                       }
        return {'masterSelections': master_data}

    def form_settings_data(self, query_id):

        self.form_properties.append((_selector('query_id'),'value',query_id,'0'))

        form_settings = {'setMaster': self.form_masters,
                         'setSelect': self.form_selections,
                         'setProp':  [dict(zip(_PROPERTY_TAGS, property_vals))\
                                      for property_vals in self.form_properties]
                         }

        client_state = self.master_select_data()
        client_state.update({'formSettings': form_settings})
        return client_state
