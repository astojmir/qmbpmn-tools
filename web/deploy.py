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

import sys
import os
import os.path
import time
import shutil
from .. import version
from ..common.utils.jinjaenv import get_jinja_env
from ..common.utils.jinjaenv import _abspath
from ..common.utils.filesys import makedirs2
from ..common.utils.filesys import copytree_filter
from ..common.utils.filesys import import_module
from .SaddleSum.validate import INITIAL_FORM_DATA
from .SaddleSum import get_etd_info
from .ITMProbe.network import ITMProbeNetwork
from .ITMProbe.display_opts import DisplayOpts
from .conf import QMBPMNSiteConf

web_package_dir = os.path.abspath(os.path.dirname(__file__))


class QMBPMNDeploy(object):

    subpackages = ['ITMProbe', 'enrich']

    def __init__(self, conf_file_json, out_stream=sys.stdout):

        self.conf = QMBPMNSiteConf(conf_file_json)
        self.conf_out_path = os.path.join(self.conf.data_root,
                                          self.conf.config_path,
                                          'config.json')
        self._out_stream = out_stream
        self.jinja_env = get_jinja_env(self.conf)

    @staticmethod
    def _get_update_time(t=None):

        t = time.localtime(t)
        return time.strftime('%B %d, %Y', t)

    def render_pages(self, subpackage):
        """
        Render all 'ordinary' html (and other) pages.
        """

        templates = getattr(self.conf, '%s_page_templates' % subpackage)
        htdocs_path = os.path.join(self.conf.site_root, \
                      getattr(self.conf, '%s_htdocs_suffix' % subpackage))
        for tmpl, name in templates:
            jt = self.jinja_env.get_template(tmpl)
            tdata = jt.render(last_updated=self._get_update_time(),
                              conf=self.conf)
            full_path = os.path.join(htdocs_path, name)
            print >>self._out_stream,  "    %s" % full_path
            yield full_path, tdata

    def render_scripts(self, subpackage):
        """
        Render scripts from templates.
        """

        templates = getattr(self.conf, '%s_scripts' % subpackage)
        htdocs_path = os.path.join(self.conf.site_root, \
                      getattr(self.conf, '%s_htdocs_suffix' % subpackage))

        for tmpl, name, context_vars in templates:
            jt = self.jinja_env.get_template(tmpl)
            tdata = jt.render(last_updated=self._get_update_time(),
                              conf=self.conf,
                              conf_path=self.conf_out_path,
                              **context_vars)
            full_path = os.path.join(htdocs_path, name)
            print >>self._out_stream,  "    %s" % full_path
            yield full_path, tdata



    def _get_networks(self):

        # Right now independent on model class
        # but that can change in future

        network_path = os.path.join(self.conf.data_root,
                                    self.conf.ITMProbe_network_dir)
        network_files = []
        for filename in os.listdir(network_path):
            if filename[-7:] == 'net.cfg':
                network_files.append(filename)
        network_files.sort()
        networks = dict(('inet%2.2d' % i, os.path.join(network_path, nf)) \
          for i,nf in enumerate(network_files))

        return networks


    def render_ITMProbe_model_pages(self):

        grp = 'grp00' # Network groups are not implemented yet.

        for model_class in self.conf.ITMProbe_imported_models:

            networks = self._get_networks()
            graph_attrs = []
            for id, nf in sorted(networks.iteritems()):
                Inet = ITMProbeNetwork(nf, init_data=False)
                graph_attrs.append({'value': id,
                                    'text': Inet.network_name,
                                    'antisinks': ' '.join(Inet.antisinks),
                                    'group': grp})

            default_display_opts = DisplayOpts(model_class._ranking_attrs,
                                               model_class._criteria,
                                               model_class._renderings)
            display_data = default_display_opts.master_select_data()

            jinja_env = get_jinja_env(self.conf)
            tmpl = jinja_env.get_template('ITMProbe/' + model_class.html_template)
            tdata = tmpl.render(conf=self.conf,
                                image_processors=DisplayOpts.image_processors,
                                graph_data=graph_attrs,
                                display_data=display_data,
                                example_data=model_class.example_data)

            full_path = os.path.join(self.conf.site_root,
                                     self.conf.ITMProbe_htdocs_suffix,
                                     model_class.input_page_name())
            print >>self._out_stream,  "    %s" % full_path
            yield full_path, tdata



    def render_enrich_form(self):
        """
        Renders the query form plus examples.
        """

        form_data = INITIAL_FORM_DATA.copy()

        htdocs_path = os.path.join(self.conf.site_root,
                                   self.conf.enrich_htdocs_suffix)

        # Get the database names from databases themselves
        # they must be present in the destination directory
        termdbs_path = os.path.join(self.conf.data_root,
                                    self.conf.enrich_termdb_dir)
        termdbs = []
        for filename in os.listdir(termdbs_path):
            if os.path.splitext(filename)[1] == '.etd':
                etd_file = os.path.join(termdbs_path, filename)
                etd_info = get_etd_info(etd_file, self.conf.saddlesum_path)
                termdbs.append((etd_info['db_name'], filename))

        termdbs.sort()
        jt = self.jinja_env.get_template('enrich/index.html')
        tdata = jt.render(last_updated=self._get_update_time(),
                          conf=self.conf,
                          termdbs=termdbs,
                          **form_data)
        full_path = os.path.join(htdocs_path, 'index.html')
        print >>self._out_stream,  "    %s" % full_path
        yield full_path, tdata

        # Now do the pre-filled example pages.
        for ex in self.conf.enrich_examples:

            selected_db = False
            # Find database
            for i, db_data in enumerate(termdbs):
                if db_data[1] == ex['database']:
                    selected_db = True
                    form_data['selected_db'] = i
                    break
            if not selected_db:
                raise RuntimeError('Could not find the database %s' % \
                                   ex['database'])
            with open(ex['filename'], 'r') as fp:
                form_data['init_weights'] = fp.read()
            form_data['cutoff_Evalue'] = ex['cutoff_Evalue']

            tdata = jt.render(last_updated=self._get_update_time(),
                              conf=self.conf,
                              termdbs=termdbs,
                              **form_data)
            full_path = os.path.join(htdocs_path, ex['page'])
            print >>self._out_stream,  "    %s" % full_path
            yield full_path, tdata



    def generate_docs(self, subpackage):
        """
        Use Sphinx to generate documentation pages from ReST input.
        """

        srcdir = getattr(self.conf, '%s_doc_source_dir' % subpackage, None)
        if srcdir is None: return

        htdocs_path = os.path.join(self.conf.site_root, \
                      getattr(self.conf, '%s_htdocs_suffix' % subpackage))

        outdir = os.path.join(self.conf.site_root, htdocs_path, \
                   getattr(self.conf, '%s_doc_suffix' % subpackage))

        from sphinx.application import Sphinx
        self._out_stream.write('** Generating documentation **\n')
        makedirs2(outdir)
        doctreedir = os.path.join(outdir, '.doctrees')

        templates_path = os.path.join(web_package_dir, 'templates/')
        app = Sphinx(srcdir, srcdir, outdir, doctreedir, 'html',
                     {'templates_path': [templates_path]},
                     sys.stdout, sys.stderr, True)
        app.builder.templates.environment.globals['conf'] = self.conf
        app.builder.templates.environment.globals['banner_links'] = \
          getattr(self.conf, '%s_banner_links' % subpackage)
        app.builder.templates.environment.globals['sidebar_blocks'] = \
          getattr(self.conf, '%s_sidebar_blocks' % subpackage)
        app.builder.templates.environment.globals['sidebar_title'] = \
          getattr(self.conf, '%s_sidebar_title' % subpackage)
        app.builder.templates.environment.filters['abspath'] = _abspath
        app.builder.build_all()

        # Remove doctreedir
        shutil.rmtree(doctreedir, True)

    def copy_static(self):
        """
        Copies all supporting files to be served over the web.
        """

        self._out_stream.write('* Copying supporting files:\n')
        for src_suffix, dest_suffix in [('static/', self.conf.static_suffix),
                                     ('netmap/', self.conf.netmap_suffix)]:

            src_dir = os.path.join(web_package_dir, src_suffix)
            dest_dir = os.path.join(self.conf.site_root, dest_suffix)
            copytree_filter(src_dir, dest_dir, ['*~', '*.svn'])


    def clean_all(self):
        """
        Cleaning all files from destination directories. This may delete files
        used by other programs.
        """

        self._out_stream.write('* Cleaning all files...\n')
        shutil.rmtree(self.conf.site_root, True)
        self._out_stream.write('     Removed %s.\n' % self.conf.site_root)

        for subpackage in self.subpackages:
            storage_dir =  getattr(self.conf, '%s_storage_dir' % subpackage, None)
            if storage_dir:
                storage_path = os.path.join(self.conf.data_root, storage_dir)
                shutil.rmtree(storage_path, True)
                self._out_stream.write('     Removed %s.\n' % storage_path)

    def write_pages(self):
        """
        Write all newly created files to htdocs_copy_root.
        """

        makedirs2(self.conf.site_root)

        # Save configuration
        makedirs2(self.conf.data_root)
        self.conf.write(self.conf_out_path)

        for subpackage in self.subpackages:
            # Temporary storage must be world writeable.
            storage_dir =  getattr(self.conf, '%s_storage_dir' % subpackage, None)
            if storage_dir:
                storage_path = os.path.join(self.conf.data_root, storage_dir)
                makedirs2(storage_path)
                os.chmod(storage_path, 0777)

            htdocs_path = os.path.join(self.conf.site_root, \
              getattr(self.conf, '%s_htdocs_suffix' % subpackage))
            makedirs2(htdocs_path)
            self._out_stream.write('* Generating scripts:\n')
            for dest_path, data in self.render_scripts(subpackage):
                with open(dest_path, 'w') as fp_out:
                    fp_out.write(data)
                os.chmod(dest_path,0755)

            self._out_stream.write('* Generating web pages:\n')
            for dest_path, data in self.render_pages(subpackage):
                with open(dest_path, 'w') as fp_out:
                    fp_out.write(data)

        self._out_stream.write('* Generating extra web pages:\n')
        for dest_path, data in self.render_enrich_form():
            with open(dest_path, 'w') as fp_out:
                    fp_out.write(data)

        for dest_path, data in self.render_ITMProbe_model_pages():
            with open(dest_path, 'w') as fp_out:
                    fp_out.write(data)


    def __call__(self, clean, generate_pages, generate_docs):

        self._out_stream.write('*** Deploying ITM Probe for the web ***\n')
        cver = version.CURRENT_VERSION
        self._out_stream.write('  * current version: %s\n' % cver)

        if clean:
            self.clean_all()
        if generate_pages:
            self.write_pages()
            self.copy_static()
        if generate_docs:
            for subpackage in self.subpackages:
                self.generate_docs(subpackage)
