Overview
========

*ITM Probe* is a an application for modeling information flow in
:term:`protein interaction networks <protein interaction network>`
based on discrete time :term:`random walks <random walk>`.

Information Flow Framework
--------------------------

Each random walk simulates a possible information path. A walker
starts at a node in the network and at each discrete time step moves
randomly to a node that is adjacent to its originating node. The
probability of moving to a particular destination node is proportional
to the weight of the link from the originating node to it. Unlike the
classical random walks, our framework allows the walker a certain
probability to :term:`dissipate <dissipation rate>`, that is, to leave
the network at each step. Each walk terminates either by dissipation
or by reaching a boundary node.

We distinguish two types of boundary nodes: :term:`sources <source>`
and  :term:`sinks <sink>`. Each source serves as origin of random
walks and hence emits information, while each sink absorbs
information. *ITM Probe* offers three models: :term:`absorbing
<absorbing model>`, :term:`emitting <emitting model>` and
:term:`channel <channel model>`.

The **emitting model** contains only sources as boundary points. For
each source *s* and any network node *i*, it returns the expected
number of visits to *i* by a random walk originating at *s*. The
**absorbing model** contains only sinks as boundary and for each
network node *j* and each sink *k* returns the likelihood of a random
walk starting at *k* to terminate at *j*.  The **normalized channel model**
contains both sources and sinks as boundary and combines the emitting
and absorbing models. It reports the normalized expected number of
visits to any node *i* from a random walk originating at a source *s* and
terminating at sink *k*. The normalization excludes the walkers that
do not reach any sink.

Each selection of boundary nodes and rates of dissipation provides the
biological :term:`context` for the information transmission
modelled. A small dissipation coefficient allows random walks to
explore the nodes farther away from their origin while a large one
means that most walks will evaporate very quickly. Since the channel
model considers only those walks that do not terminate due to
dissipation, the large dissipation values will illuminate the nodes on
the shortest paths from sources to sinks. The dissipation coefficients
may be specified directly or through an
:ref:`alternative criterion <dissipation-criterion-label>`.

We call the set of most significant nodes (with respect to the number
of visits, in the case of the emitting and channel models, or the
absorption probability, in the case of the absorbing model) an
*Information Transduction Module* (:term:`ITM`).


.. _dissipation-criterion-label:

Alternative Ways of Specifying Dissipation
------------------------------------------

For the **absorbing model**, the alternative to specifying the
dissipation coefficient directly is to set the average absorption
probability. The average absorption probability is calculated by
taking the probability of absorption at the sinks for every transient
node connected to sinks, and averaging it by the number of transient
nodes and the total number of sinks. It thus represents the likelihood
of a random walk starting at a randomly selected point in the network
to reach a sink. Every dissipation coefficient between 0 and 1 has a
corresponding average absorption probability and hence specifying a
valid absorption probability indirectly specifies the dissipation
coefficient. The dissipation coefficient obtained in this way is
larger if the sinks are well-connected hubs near the centre of the
network as sinks, in contrast to the case when the chosen sinks are
not as well connected.

In the case of the **emitting model**, the dissipation coefficient can
be specified through the average path length. The average path length
represents the average length of the path that a random walk
originating at a source travels before dissipating. There is a
one-to-one correspondence between path lengths and dissipation
coefficients.

The node dissipation coefficient for the **channel model** can be
specified through the amount of drift (deviation) from the
shortest path length from sources to sinks. Since the channel model
concerns only those random walks that originate at the specified
sources and terminate at specified sinks, the minimum distance a
random walk can take (at full dissipation) is the smallest length of
the shortest path from one source to one sink. Allowing deviations
from the shortest path corresponds to smaller dissipation. It is
possible to express the drift from the shortest path in absolute or
relative (in terms of the length of the shortest path) units.




ITM Probe Software
------------------

*ITM Probe* can be used through three interfaces: command line
(*qmbpmn-tools* package), web and as a
`Cytoscape <http://www.cytoscape.org/>`_ plugin.

The standalone version is written in the Python programming language
and is a part of the *qmbpmn-tools* package, which contains additional
utilities. The package has numerous dependencies including Numpy,
Scipy, UMFPACK, Jinja2, Sphinx and Graphviz. The source code is made
freely available but the package is in heavy development, lacks full
documentation and is not supported in any way. Only the users who wish
to examine the source code for *ITM Probe* algorithms or to reproduce
the webpages of the QMBP molecular network tools (*ITM Probe* and
*SaddleSum* locally) should download and attempt to install
*qmbpmn-tools*.

The web version provides access to *ITM Probe* through a web
form. The users are restricted to querying only the few compiled
protein interaction networks from model organisms networks available
on the website. The server-side scripts are part of the *qmbpmn-tools*
package and rely the Graphviz suite for visualizing *ITM Probe* results.

Cytoscape is an open source platform for complex network analysis and
visualization written in Java programming language. Apart for a rich
set of graph visualization tools, it provides an interface for
externally written plugins that provide additional functionality such
as network analysis algorithms, database import and functional
enrichment analysis. Cytoscape users are therefore able to combine
algorithms and data from different sources to perform complex
network-based analyses.

*CytoITMprobe* is a Cytoscape plugin that enables *ITM Probe* queries
from Cytoscape platforms. It can interact either with a locally
installed command-line program directly, or through the QMBP web
server. Any Cytoscape network can be passed to *ITM Probe*. The output
is written as the node attributes of the query network, which can be
manipulated further within Cytoscape.


..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
