Interaction Graph
^^^^^^^^^^^^^^^^^

While the mathematical framework of *ITM Probe*  can be applied to any directed
graph, the web service presently supports only the yeast
(*Saccharomyces cerevisiae*), human (*Homo sapiens*), fruit fly
(*Drosophila melanogaster*) and flatworm (*Caenorhabditis elegans*) physical
interaction networks derived from  `the BioGRID <http://www.thebiogrid.org>`_
database. We plan to offer more networks in future.

The *ITM Probe* web service offers three types of networks: **Full**,
**Reduced** and **Directed**. Presently, all supported organisms have Full
networks, while the Reduced and Directed types are available only for yeast as
it has the network with by far the best quality and coverage. All physical
interaction networks from the BioGRID contain the following interaction types:
'Affinity Capture-MS', 'Affinity Capture-RNA', 'Affinity Capture-Western',
'Co-crystal Structure', 'Co-fractionation', 'Co-localization',
'Co-purification', 'FRET', 'Far Western', 'Reconstituted Complex', 'Two-hybrid',
'PCA' and 'Biochemical activity'.

Full networks contain all interactions from the BioGRID for a particular
species. All interaction types are treated as undirected and given a weight 1.0
independently of the number of publications reporting the same interaction.

Reduced networks are derived from Full by filtering out those interactions that
are reported solely by high-throughput studies (that is, by publications
reporting more than 300 interactions). The interactions reported by more than
one publication are not filtered out. For yeast, we also do not filter the
interactions reported by *Collins et al. (2007)* (`PMID: 17200106
<http://www.ncbi.nlm.nih.gov/sites/entrez?term=17200106>`_) and by *Tarassov et
al. (2008)* (`PMID: 18467557
<http://www.ncbi.nlm.nih.gov/sites/entrez?term=18467557>`_), because they use
newer experimental techniques (as opposed to two-hybrid) and because their
reported interactions are generally verified by more than a single
experiment. As for Full networks, the edges of Reduced networks are all
undirected with weight 1.0.

Directed networks are obtained from Reduced by turning all 'Biochemical
activity' (phosporylation, ubiquitination etc.) interactions into directed links
(bait to prey). Interactions are divided into two groups, 'Biochemical activity'
ones and all others, and independently filtered by throughput as for Reduced
network (hence we accept a 'Biochemical activity' interaction from a
high-throughput study only if another 'Biochemical activity' link is reported by
another publication for the same pair). Then, those interactions from the 'other'
group that have an accepted corresponding 'Biochemical activity' link are
removed. Finally the filtered 'Biochemical activity' interactions are introduced
into the graph as directed links with weight 2.0 and all remaining interactions
are taken as undirected with weight 1.0. In this way, Directed networks favor
the 'Biochemical activity' and are therefore better than Full or Reduced for
investigating potential signalling cascades.

The supported yeast networks also supply the list of about 170 :term:`excluded
nodes <Excluded node>`, representing the cytoskeleton proteins, histones and
chaperones that may provide undesirable shortcuts. The networks from other
species do not have default excluded nodes but users can enter their own sets,
if they wish so.



..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
