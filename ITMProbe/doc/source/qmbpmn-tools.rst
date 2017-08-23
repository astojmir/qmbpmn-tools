.. _qmbpmn-tools-label:

Python Package - qmbpmn-tools
=============================

*qmbpmn-tools* is a collection of Python libraries and scripts for
network analysis developed by the QMBP group at the NCBI. It consists
of the *ITM Probe* library and executable script, the routines for
managing *ITM Probe* and *SaddleSum* web sites, a package manager and
miscellaneous libraries and utilities.


.. warning:: *qmbpmn-tools* is in heavy development and may change in
             many ways. We do not support this package but only
             release it as a reference implementation. This
             documentation is therefore incomplete and should be
             considered as short installation notes rather than as
             user's manual. The best way to obtain detailed
             information is to actually read the source code.

Prerequisites
-------------

*qmbpmn-tools* requires a number of standalone programs and Python
packages. All are open source and can be downloaded and installed on
UNIX, Windows and Mac OSX machines. Please consult the documentation
of individual packages for information of how to install them. The
prerequisites are:

* `Python <http://www.python.org/>`_ 2.6 or 2.7 complied with `SQLite
  <http://www.sqlite.org/>`_ support. Python 3 is not yet supported.

* `SaddleSum
  <http://www.ncbi.nlm.nih.gov/CBBresearch/Yu/downloads/saddlesum.html>`_
  standalone program for *SaddleSum* website functionality.

* `Graphviz <http://www.graphviz.org/>`_ graph visualization
  software. **Not necessary for CytoITMprobe**.

* `Numpy and Scipy <http://www.scipy.org/>`_ libraries of scientific
  tools for Python. Numpy should be version 1.3 or higher, while Scipy
  should be version 0.7 or higher.

* `SciKits.umfpack <http://scikits.appspot.com/umfpack>`_ Python
  package (**Optional but highly recommended**). It requires
  `UMFPACK <http://www.cise.ufl.edu/research/sparse/umfpack>`_
  library for solving sparse systems of linear equations. Ensure
  that UMFPACK is compiled with good BLAS, otherwise ITM Probe
  performance will greatly suffer.

* `Jinja2 <http://jinja.pocoo.org/2/>`_ template engine. **Not
  necessary for CytoITMprobe**.

* `Sphinx <http://sphinx.pocoo.org/index.html>`_ Python documentation
  generator (version 1 or higher). Sphinx additionally requires
  `docutils <http://docutils.sourceforge.net/>`_ and
  `Pygments <http://pygments.org/>`_ packages. **Not necessary for CytoITMprobe**.


Downloading and Installing
--------------------------

The source code is available on the NCBI FTP site
(ftp://ftp.ncbi.nih.gov/pub/qmbpmn/qmbpmn-tools/) as a tar.gz
archive. Extract the archive to a temporary directory, and install it
in the standard way::

  python setup.py install

The setup program will install the package and also place several
executable scripts in your path.


Components
----------

*qmbpmn-tools* source package consists of four subdirectories:

* **scripts/** contains executable programs (i.e. Python scripts) such as

  * ``itmprobe`` - standalone *ITM Probe*,
  * ``qmbpmn-deploy`` - a script to deploy the website,
  * ``qmbpmn-server`` - a rudimentary deployment server,
  * ``qmbpmn-datasets`` - package manager

Most scripts have some help available. Use::

  <script-name> -h

to print help to the screen.

* **ITMProbe/** contains *ITM Probe* core library

* **web/** contains Python and resource files for the *ITM Probe* and
  *SaddleSum* web sites.

* **common/** contains shared subpackages as well as code obtained
  from other open-source projects.



..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
