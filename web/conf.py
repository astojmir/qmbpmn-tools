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
from urlparse import urljoin
from ..common.utils.dataobj import restore_data_object, save_data_object
from ..common.utils.filesys import import_module
from .. import __file__ as _qmbpmn_file

class QMBPMNSiteConf(object):
    """ Contains the web site configuration."""

    def __init__(self, conf_file_json, restore=False):

        if restore:
            self.__dict__.update(restore_data_object(conf_file_json))
            # Need to recreate ITMProbe_imported_models
            self._get_ITMProbe_models()
            return

        self.qmbpmn_root = os.path.dirname(_qmbpmn_file)

        # Load default options
        config_dir = os.path.join(self.qmbpmn_root, 'web', 'config')
        default_file_json = os.path.join(config_dir, 'default.json')
        default_dict = restore_data_object(default_file_json)

        # Find config file
        conf_file = None
        conf_search_order = [conf_file_json,
                             os.path.join(os.path.expanduser('~'),
                                          '.qmbpmn', conf_file_json),
                             os.path.join(config_dir, conf_file_json),
                             ]
        for f in conf_search_order:
            if os.path.exists(f):
                conf_file = f
                break
        if conf_file is None:
            raise RuntimeError("Cannot find config file %s" % conf_file)

        # Import JSON file and insert into instance dict
        specific_dict = restore_data_object(conf_file)
        default_dict.update(specific_dict)

        self.__dict__.update(default_dict)


        # Ensure that SaddleSum source code directory is specified
        if self.enrich_source_root is None:
            raise RuntimeError('SaddleSum source directory not specified as ' \
                               'the config parameter "enrich_source_root".')

        # Process special cases
        self._get_ITMProbe_models()
        self._adjust_ITMProbe_links()
        self._adjust_ITMProbe_doc_sources()
        self._adjust_SaddleSum_links()
        self._adjust_SaddleSum_doc_sources()
        self._adjust_SaddleSum_examples()

    def write(self, out_file):

        config_dict = self.__dict__.copy()
        # ITMProbe_imported_models are not JSON serializable
        del config_dict['ITMProbe_imported_models']
        save_data_object(config_dict, out_file)

    def _module_path(self, path_list):

        if path_list is None:
            return None
        path_list = [self.qmbpmn_root] + path_list
        return os.path.join(*tuple(path_list))

    def _get_ITMProbe_models(self):

        self.ITMProbe_imported_models = []
        for module_name, class_name, opts in self.ITMProbe_models:
            module = import_module(module_name)
            model_class = getattr(module, class_name)
            for attr, val in opts.iteritems():
                setattr(model_class, attr, val)
            self.ITMProbe_imported_models.append(model_class)

    def _adjust_ITMProbe_links(self):

        self.ITMProbe_banner_links[1] = urljoin(self.ITMProbe_htdocs_suffix,
                                                self.ITMProbe_banner_links[1])

        for i in xrange(len(self.ITMProbe_sidebar_blocks)):
            title, page, sublinks = self.ITMProbe_sidebar_blocks[i]
            link_prefix = self.ITMProbe_htdocs_suffix
            if title == 'WEB SERVICE':
                for mc in self.ITMProbe_imported_models:
                    sublinks.append([mc.html_text, mc.input_page_name()])
            elif title == 'DOCUMENTATION':
                link_prefix = urljoin(self.ITMProbe_htdocs_suffix,
                                      self.ITMProbe_doc_suffix)

            if self.ITMProbe_sidebar_blocks[i][1] is not None:
                self.ITMProbe_sidebar_blocks[i][1] = \
                  urljoin(link_prefix, self.ITMProbe_sidebar_blocks[i][1])
            for j in xrange(len(sublinks)):
                sublinks[j][1] = urljoin(link_prefix, sublinks[j][1])

    def _adjust_ITMProbe_doc_sources(self):

        self.ITMProbe_doc_source_dir = \
          self._module_path(self.ITMProbe_doc_source_dir)

    def _adjust_SaddleSum_doc_sources(self):

        self.enrich_doc_source_dir = os.path.join(self.enrich_source_root,
                                                  self.enrich_doc_source_dir)

    def _adjust_SaddleSum_links(self):

        self.enrich_banner_links[1] = urljoin(self.enrich_htdocs_suffix,
                                              self.enrich_banner_links[1])

        for i in xrange(len(self.enrich_sidebar_blocks)):
            title, page, sublinks = self.enrich_sidebar_blocks[i]
            link_prefix = self.enrich_htdocs_suffix
            if title == 'DOCUMENTATION':
                link_prefix = urljoin(self.enrich_htdocs_suffix,
                                      self.enrich_doc_suffix)

            if self.enrich_sidebar_blocks[i][1] is not None:
                self.enrich_sidebar_blocks[i][1] = \
                  urljoin(link_prefix, self.enrich_sidebar_blocks[i][1])
            for j in xrange(len(sublinks)):
                sublinks[j][1] = urljoin(link_prefix, sublinks[j][1])

    def _adjust_SaddleSum_examples(self):

        for exmpl in self.enrich_examples:
            exmpl['cutoff_Evalue'] = float(exmpl['cutoff_Evalue'])
            exmpl['filename'] = os.path.join(self.enrich_source_root, exmpl['filename'])
