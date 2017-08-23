Additional Information
======================

License
-------

All code for *ITM Probe* (*qmbpmn-tools*) and *CytoITMProbe* written
at the NCBI is released into Public Domain. The licenses of external
components are indicated in the source packages.

References
----------

Further details about *ITM Probe* can be found in the following references:


1. A. Stojmirovic and Y.-K. Yu. Information flow in interaction networks.
   *J. Comput. Biol.*, **14** (8):1115-1143, 2007.
2. A. Stojmirovic and Y.-K. Yu. ITM Probe: analyzing information flow in protein networks.
   *Bioinformatics*, **25** (18):2447-2449, 2009.

Credits
-------

  * Aleksandar Stojmirovic and Yi-Kuo Yu designed the study, conducted the research and wrote the papers;
  * Aleksandar Stojmirovic wrote the code for the *qmbpmn-tools*.
  * Alexander Bliskovsky and Aleksandar Stojmirovic wrote together the
    code for *CytoITMProbe*.

Acknowledgments
---------------

*ITM Probe* (*qmbpmn-tools* package) is written in the `Python <http://www.python.org/>`_ programming
language and relies on several open-source components:

  * `Numpy and Scipy <http://www.scipy.org/>`_ libraries of scientific tools for Python;
  * `UMFPACK <http://www.cise.ufl.edu/research/sparse/umfpack>`_ library for solving sparse systems of linear equations;
  * `Graphviz <http://www.graphviz.org/>`_ graph vizualization software;
  * `Sphinx <http://sphinx.pocoo.org/index.html>`_ Python documentation generator;
  * `Jinja2 <http://jinja.pocoo.org/2/>`_ template engine.

The web browser client code uses various Javascript routines from the
NCBI. ECMAScrpit code and widgets for the SVG 'Network Navigator' were taken
from `Carto:Net <http://www.carto.net/>`_.

All discrete network image color schemes were taken from the
`www.ColorBrewer.org <http://www.ColorBrewer.org>`_ site by
Cynthia A. Brewer, Geography, Pennsylvania State University.

Protein interaction graphs for the web version were constructed using
data from the  `BioGRID <http://www.thebiogrid.org/>`_ database.

*CytoITMProbe* uses
`Apache HttpComponents <http://hc.apache.org/>`_ library for HTTP
requests and `Google gson <http://code.google.com/p/google-gson/>`_
for manipulating JSON files. The icons used in the graphical interface
were taken from the `Tango Icon Library <http://tango.freedesktop.org/Tango_Icon_Library>`_, version 0.8.90.

We are grateful to Zvezdana Stojmirovic for help with the graphic design the
*ITM Probe* web pages and interfaces.


News and Updates
----------------

  * **03-Jul-2013.** *qmbpmn-tools* 1.5.3 released - minor changes and bug fixes.
  * **12-Mar-2012.** *CytoITMprobe* 1.5 released.
  * **02-Mar-2012.** *qmbpmn-tools* 1.5.2 released - a bug fix for *ITM Probe*.
  * **07-Feb-2012.** *qmbpmn-tools* 1.5.1 released - minor changes and bug fixes for *ITM Probe*.
  * **14-Dec-2011.** *qmbpmn-tools* 1.5.0 released - minor changes mostly related to *SaddleSum*.
  * **11-Jul-2011.** *ITM Probe* 1.3.0 released, with updated web forms. It is now possible to retrieve an old job using its query ID.




..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
