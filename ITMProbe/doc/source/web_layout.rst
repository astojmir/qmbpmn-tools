Layout options
""""""""""""""

The **Layout by** selection box specifies the choice of the ranking criterion
for selecting the most significant nodes. At present, the choice is restricted
to a :term:`Total visits` and :term:`Interference` for the channel and emitting
models and :term:`Total Likelihood` for the absorbing model.

The **Criterion** selection box specifies the criterion used to select the
number of top ranking nodes to be shown. The default option for the channel and
emitting models is :term:`Participation ratio`. Other options are *Maximum
nodes* (the fixed number of nodes specified by the **Maximum Nodes** option is
shown) or *Cutoff Value* (the nodes having the associated value specified in the
**Layout by** box greater than the **Cutoff Value** are displayed), the default
for the absorbing model.

The **Maximum Nodes** option specifies the maximum number of nodes to be shown,
capped by 200. This option overrides the number obtained from the **Criterion**
selection in case of the *Participation ratio* or the number of nodes above the
*Cutoff Value* are too large.

The placement of nodes in the graphical image is determined according to
the **Layout Seed** option. Each seed produces a different layout and hence it
may be possible to obtain a better image of and ITM by changing this parameter
from its default value and trying several different seed values.


..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
