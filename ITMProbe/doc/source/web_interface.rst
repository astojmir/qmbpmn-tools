Web Service
===========

The web interface for *ITM Probe* consists of a query submission page
and a results page. The query page is divided into two panels: Model
Parameters,and Display Parameters, while the results page contains
Display Parameters and Results pannels, plus a form allowing
submission of the results to *SaddleSum*, our term enrichment analysis
tool. Each model (channel, emitting or absorbing) uses a different
page for query submission, with a slightly different Model Parameters
panel.

To run an *ITM Probe* query, first select the desired model page (from
`the main page
<http://www.ncbi.nlm.nih.gov/CBBresearch/Yu/mn/itm_probe/index.html>`_). In
the Model Parameters panel, select the interaction graph and excluded
nodes (either by entering them directly or by uploading a
text file with one node per line), and then set the contexts. When
finished, press the **RUN** button to submit the query.

The output of *ITM Probe* consists of the graphical representation of
the resulting ITM, query-related summary statistics and a table
listing the top ranking members of the ITM. The number of members of
ITM to be shown as well as the type of the graphical representation are
controlled through Display Parameters panel, either on the query
submission or on the results page. Thus, it is possible to run a
single query and then explore different aspects of the results using
different display options.


.. toctree::
   :maxdepth: 1

   web_modelopts.rst
   web_displayopts.rst
   web_results.rst
   web_analysis.rst



..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
