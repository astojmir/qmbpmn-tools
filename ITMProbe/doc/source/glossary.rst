.. _glossary:


Glossary
========

.. glossary::

  Absorbing model
      Corresponds to absorbing Markov chains. Contains only sinks as
      boundary and for each node in the network evaluates the
      likelihood for a random walk starting at that node to terminate
      at each sink while avoiding all other sinks (hence the sinks can
      be thought of as competing for the flow). The total likelihood
      at each node is the sum of the individual likelihoods for all
      sinks. Due to dissipation, the total likelihood at each node can
      be much less than 1, especially for the nodes far from any of
      the sinks.

  Channel model
     Contains both sources and sinks and combines emitting and
     absorbing models. It reports the total expected number of visits
     to any node in the network from a random walk originating at each
     source and terminating at any of the sinks (i.e. not
     dissipating).

  Context
      A set of parameters that defines the environment for a random
      walk in an interaction graph. It includes boundary nodes (sources
      and/or sinks), rate of dissipation and the set of excluded
      nodes. *ITM Probe* evaluates the context to describe the
      information flow it represents.

  Dissipation rate
       Also known as termination/stopping probability.
       A parameter between 0 and 1 describing the proportion of random
       walks that leave the network (evaporate) at each step. The
       higher the dissipation rate, the more likely it is for the
       random walk to terminate close to its origin and thus have only
       local effects. In the context of the channel model, the
       dissipation rate controls the likelihood for the random walk to
       visit the nodes away from the shortest paths from sources to
       sinks -- dissipation close to 1 means that only the nodes on
       shortest paths will be visited.

  Emitting model
      Contains sources on the boundary. For each node in the network
      evaluates the average number of time the node is visited by a
      random walk originating at each source. Random walks terminate
      when reaching any source or dissipating.

  Excluded node
      A protein node that is excluded from consideration during a run
      of *ITM Probe*.

      In some cases, proteins with a large number of non-specific
      interaction partners might overtake the true signaling proteins in
      the information flow modeling.  Therefore, *ITM Probe* allows
      users to specify nodes to exclude from the network. For the
      yeast network the nodes excluded by default include cytoskeleton
      proteins, histones and chaperones, since they may provide
      undesirable shortcuts.

      Note that excluded nodes are treated as terminating points for
      random walks: the edges leading into them are not deleted but
      any random walk entering and excluded node evaporates instead.

  Interaction network
      A (weighted, directed) graph whose nodes (vertexes) represent
      agents and edges (links) are interactions. Thus, two agents are
      linked if they interact in some way. The weight of a link
      corresponds to the strength of the corresponding interaction.

  Interference
      A concept used in the context of the emitting and the channel
      model to describe the measure of overlap between visits of each
      node by random walks originating at different sources. Large
      interference implies large overlap between flows from different
      sources while small interference means little overlap.

  ITM
      **I**\nformation **T**\ransduction **M**\odule. The set of most
      significant nodes (with respect to the number of visits, in the case
      of the emitting and channel models, or the absorption probability,
      in the case of the absorbing model) resulting from the query context
      of *ITM Probe*.

  Participation ratio
      Used for the emitting and the channel model. Gives approximate
      number of nodes that have a significant (that is, much larger
      than ordinary) total number of visits.

  Protein interaction network
      An interaction network where nodes correspond to cellular
      proteins. The edges may represent a variety of interactions, for
      example: physical (protein A binds protein B), metabolic (A and
      B catalyze reactions involving the same chemical), genetic (A
      and B are expressed together) or biochemical (A
      post-translationally modifies B). It is also possible to include
      more than one type of interaction in the network, depending on
      the problem being modelled.

  Random walk
      A mathematical concept involving an entity that moves about a
      given space in a random fashion. In the context of graphs, a
      random walk describe a process where a \'walker\' moves from one
      vertex into another with a probability proportional to the
      weight of the edge connecting them. This process is equivalent
      to a Markov chain on the vertex set. A random walk starts at a
      node in a network and moves about visiting different nodes until
      it terminates. It can terminate either at a boundary point
      (source or sink) or by leaving the network due to dissipation.

  Sink
      A destination of a random walk.

  Source
      A point of origin of a random walk.

  Termination probability
      see :term:`Dissipation rate`.

  Total likelihood
      see :term:`Absorbing model`.

  Total visits
      Used in the context of the emitting and the channel model to
      denote the total number of visits from all sources.



..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
