# -*- coding: utf-8 -*-
#
# ITM Probe documentation build configuration file, created by
# sphinx-quickstart on Mon Oct 27 12:05:04 2008.
#
# This file is execfile()d with the current directory set to its containing dir.
#
# The contents of this file are pickled, so don't put values in the namespace
# that aren't pickleable (module imports are okay, they're removed automatically).
#
# All configuration values have a default value; values that are commented out
# serve to show the default value.

import sys, os
from qmbpmn.version import CURRENT_VERSION, SHORT_VERSION

# If your extensions are in another directory, add it here. If the directory
# is relative to the documentation root, use os.path.abspath to make it
# absolute, like shown here.
#sys.path.append(os.path.abspath('some/directory'))

# General configuration
# ---------------------

# Add any Sphinx extension module names here, as strings. They can be extensions
# coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = ['sphinx.ext.pngmath']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['.templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General substitutions.
project = u'ITM Probe'
copyright = u''

# The default replacements for |version| and |release|, also used in various
# other places throughout the built documents.
#
# The short X.Y version.
version = SHORT_VERSION
# The full version, including alpha/beta/rc tags.
release = CURRENT_VERSION

# There are two options for replacing |today|: either, you set today to some
# non-false value, then it is used:
#today = ''
# Else, today_fmt is used as the format for a strftime call.
today_fmt = '%B %d, %Y'

# List of documents that shouldn't be included in the build.
#unused_docs = []

# List of directories, relative to source directories, that shouldn't be searched
# for source files.
exclude_trees = []

# The reST default role (used for this markup: `text`) to use for all documents.
#default_role = None

# If true, '()' will be appended to :func: etc. cross-reference text.
#add_function_parentheses = True

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
#add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
#show_authors = False

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'


# Options for HTML output
# -----------------------

html_theme = 'basic'
html_theme_options = {}

# html_theme_path = []
# html_style = []

html_title = 'ITM Probe Documentation'
# html_short_title = None
# html_logo = None
# html_favicon = None
html_static_path = []
html_last_updated_fmt = '%b %d, %Y'
html_use_smartypants = True
html_add_permalinks = False
html_sidebars = {
   '**': ['relations.html', 'sourcelink.html', 'searchbox.html'],
}
# html_additional_pages = {}
html_domain_indices = False
html_use_modindex = False
html_use_index = False
html_split_index = False
html_copy_source = True
html_show_sourcelink = True
# html_use_opensearch = ''
html_file_suffix = '.html'
html_link_suffix = '.html'
html_translator_class = None
html_show_copyright = False
html_show_sphinx = False
html_output_encoding = 'utf-8'
html_compact_lists = True
html_secnumber_suffix = ". "
htmlhelp_basename = 'ITMProbedoc'


# Options for LaTeX output
# ------------------------

# The paper size ('letter' or 'a4').
latex_paper_size = 'letter'

# The font size ('10pt', '11pt' or '12pt').
latex_font_size = '11pt'

# Grouping the document tree into LaTeX files. List of tuples
# (source start file, target name, title, author, document class [howto/manual]).
latex_documents = [
  ('index', 'ITMProbe_manual.tex', u'ITM Probe Documentation',
   u'Aleksandar Stojmirovic', 'howto', True),
]

# The name of an image file (relative to this directory) to place at the top of
# the title page.
latex_logo = '02C.png'

# For "manual" documents, if this is true, then toplevel headings are parts,
# not chapters.
latex_use_parts = False

# Additional stuff for the LaTeX preamble.
latex_preamble = \
r"""
\makeatletter
\renewcommand{\tableofcontents}{
  \begingroup
    \parskip = 0mm
    \py@OldTableofcontents
  \endgroup
  \vspace{12pt}
}
\let\stdsection=\section
\renewcommand\section{\newpage\stdsection}
\pagenumbering{arabic}
\pagestyle{plain}
\thispagestyle{plain}
\makeatother
"""

# Documents to append as an appendix to all manuals.
#latex_appendices = ['saddlesum-cli', 'saddlesum-show-etd']

# If false, no module index is generated.
latex_use_modindex = False
latex_domain_indices = False
latex_show_pagerefs = True
latex_show_urls = 'inline'

latex_elements = {'printindex': ''}

latex_elements = {}
