
Rendering options
"""""""""""""""""

The **Color by** selection box specifies the criterion for coloring the
nodes. When only a single source or sink are present only the *Total Visits*
(for the channel and emitting models) and *Total Likelihood* (for the absorbing
model) criteria are available. When multiple boundary points are specified, it
is possible to color the nodes according to the values associated with a single
boundary point or according to the :term:`Interference` at that node.
Furthermore, if there are less than four boundary nodes, the
*Intensities (color mixture)* option becomes available. In this case, each
source (in the channel or emitting model) or sink (in the absorbing model) is
assigned a basic CMY color and the coloring of each displayed node is a result
of mixing the colors corresponding to its model values for each of the boundary
points.

The **Scaling** selection box determines the scaling function applied to the
node intensities before coloring, while the **Colormap** specifies the set of
colors used to describe node values.

Each graphical layout can be rendered and saved in multiple formats
(SVG, PNG, JPEG, EPS and PDF), selected in the **Image Format** box. The *SVG in
Navigator* option produces an image of the ITM embedded into the *Network
Navigator*, which allows scrolling and zooming the image.


..
   Local Variables:
   mode: rst
   indent-tabs-mode: nil
   sentence-end-double-space: t
   fill-column: 70
   End:
