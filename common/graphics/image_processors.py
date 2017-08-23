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

"""Processors of images output by Graphviz programs."""

from subprocess import Popen, PIPE
from xml.dom import minidom
from ...common.utils.jinjaenv import get_jinja_env

def optional_http_header(meth):
    """ Decorator to optionally write http header before anything else."""
    def _new_process_stream(self, fp_in, fp_out, legend_items=None):
        if self.write_http_header:
            fp_out.write(self.http_header)
        return meth(self, fp_in, fp_out, legend_items)
    return _new_process_stream

class BasicOutputImage(object):
    """Basic image processor that does not do any processing."""

    def __init__(self, name, text, mime_type, write_http_header=True):

        self.name = name
        self.text = text
        self.mime_type = mime_type
        self.neato_option = '-T%s' % name
        self.write_http_header = write_http_header
        self.http_header = "Content-Type: %s\n\n" % self.mime_type

    @optional_http_header
    def process_stream(self, fp_in, fp_out, legend_items=None):
        """Process the image from fp_in, outputting to fp_out.

        * legend_items (optional) a tuple of two lists of same size,
            color_list and boundaries, that supply the list of colors and
            boundaries between them to be used when constructing a legend
            for the image. At this moment only SVGNavigatorOutputImage adds
            a legend.
        """
        fp_out.write(fp_in.read())

    def html(self, url):
        """HTML tag for the image to be inserted in output HTML page.

        Used by ITMProbe.
        """
        return '<img class="solid-bg" src="%s" alt="ITM image (%s)"/>' % \
               (url, self.text)

class SVGOutputImage(BasicOutputImage):
    """Processor for image in SVG format."""

    @staticmethod
    def _get_image_DOM(fp_in, stroke_width=0.3):
        image_DOM = minidom.parse(fp_in)
        image_DOM.normalize()
        img_doc = image_DOM.documentElement
        G = img_doc.getElementsByTagName('g')[0]

        # Set stroke-width for the graph (edges + node frames)
        if stroke_width != None:
            G.setAttribute('style', 'stroke-width:%.3fpx;' % stroke_width)

        # Fix a bug (either by graphviz or firefox, depending on the point
        # of view) that makes the node labels too large. The problem is that
        # SVG text font-size style attribute does not have units attached.

        # We fix it by getting the font-size from each of the labels, checking
        # if it has units and, if not, inserting 'px' next to it.
        for txt_node in G.getElementsByTagName("text"):
            font_size = 0.0
            styles = txt_node.getAttribute('style').split(';')

            for i, stl in enumerate(styles):
                stl_props = stl.split(':')
                if stl_props[0] == 'font-size':
                    try:
                        font_size = float(stl_props[1])
                        if font_size > 0.0:
                            styles[i] = 'font-size:%.2fpx' % font_size
                            txt_node.setAttribute('style', ';'.join(styles))
                    except ValueError:
                        pass
                    break

        return image_DOM

    @optional_http_header
    def process_stream(self, fp_in, fp_out, legend_items=None):
        image_DOM = self._get_image_DOM(fp_in)
        fp_out.write(image_DOM.toxml("utf-8"))
        image_DOM.unlink()

    def html(self, url):
        return '<embed class="solid-bg" src="%s" type="%s"' \
               ' width="620" height="500"/>' % (url, self.mime_type)

class EPSOutputImage(BasicOutputImage):
    """Processor for image in postscript format."""
    def __init__(self, name, text):
        BasicOutputImage.__init__(self, name, text, 'application/postscript')
        self.neato_option = '-T%s' % 'ps2'
        self.http_header = "Content-Type: %s\n" % self.mime_type
        self.http_header += "Content-Disposition: attachment;" \
                            " filename=itm_probe_results.eps\n\n"

    def html(self, url):
        msg = 'Click here to download the EPS image.'
        return '<a href="%s" type="%s" target="_blank">%s</a>' % \
               (url, self.mime_type, msg)


class PDFOutputImage(BasicOutputImage):
    """Processor for image in PDF format.

    Uses ps2pdf to convert postscript to pdf.
    """
    def __init__(self, name, text):
        BasicOutputImage.__init__(self, name, text, 'application/pdf')
        self.neato_option = '-T%s' % 'ps2'
        self.http_header = "Content-Type: %s\n" % self.mime_type
        self.http_header += "Content-Disposition: attachment;" \
                            " filename=itm_probe_results.pdf\n\n"

    @optional_http_header
    def process_stream(self, fp_in, fp_out, legend_items=None) :

        command = '/usr/bin/ps2pdf - -'
        with open('/dev/null', 'w') as FNULL:
            p = Popen(command, shell=True, bufsize=0,
                      stdin=PIPE, stdout=PIPE, stderr=FNULL, close_fds=True)
            p.stdin.write(fp_in.read())
            p.stdin.close()

        fp_out.write(p.stdout.read())

    def html(self, url):
        msg = 'Click here to download the image in PDF format.'
        return '<a href="%s" type="%s" target="_blank">%s</a>' % \
               (url, self.mime_type, msg)


class SVGNavigatorOutputImage(SVGOutputImage):
    """Processor for image in SVG format embedded into a navigator."""

    def __init__(self, text, navigator_options=None, jinja_env=None,
                 template='termmap.svg', write_http_header=True):

        SVGOutputImage.__init__(self, 'netmapsvg2', text, "image/svg+xml",
                                write_http_header)

        self.neato_option = '-T%s' % 'svg'
        self.jinja_env = get_jinja_env() if jinja_env is None else jinja_env
        self.template = template

        nav_opts = {'script_path': 'netmap/',
                    'map_title': 'Term Navigator',
                    'tools_title': 'NETWORK NAVIGATOR',
                    'image_view': (620, 500),
                    'mainMap_pos': (0,15),
                    'mainMap_view': (400,480),
                    'refMap_pos': (415,93),
                    'refMap_scale': 0.3333333,
                    'zoom_factor': 0.75,
                    'zoom_levels': 10,
                    'toolbar_pos': (415,48),
                    'legend_pos': (415,285),
                    'vertical_legend': True,
                    'node_legend_pos': (520, 295),
                    }
        if navigator_options is not None:
            nav_opts.update(navigator_options)
        self.navigator_options = nav_opts


    @optional_http_header
    def process_stream(self, fp_in, fp_out, legend_items=None):

        image_DOM = self._get_image_DOM(fp_in)
        img_doc = image_DOM.documentElement

        # process image_DOM: get bounding box and scale appropriately
        pts = image_DOM.documentElement.getAttribute('viewBox').split(' ')
        x, y, w, h = map(float, pts)
        w = w - x
        h = h - y
        scale = min(self.navigator_options['mainMap_view'][0]/w,
                    self.navigator_options['mainMap_view'][1]/h)

        G = img_doc.getElementsByTagName('g')[0]
        transform = G.getAttribute('transform')
        G.setAttribute('transform', "scale(%.5f %.5f) %s" % \
                       (scale, scale, transform))
        img_doc.setAttribute('height', '%.5f' % (scale*h))
        img_doc.setAttribute('width', '%.5f' % (scale*w))

        image_DOM.documentElement.removeAttribute('viewBox')

        # Main Map
        mainMap_content = image_DOM.documentElement.toxml("utf-8")

        # Reference Map - text nodes are removed
        for node in image_DOM.getElementsByTagName("text"):
            node.parentNode.removeChild(node)
        refMap_content = image_DOM.documentElement.toxml("utf-8")
        image_DOM.unlink()

        # Format legend boundary strings
        if legend_items is not None:
            boundaries = list(reversed(['%.1e' % x for x in legend_items[1]]))
            color_list = list(reversed(legend_items[0]))
        else:
            boundaries = []
            color_list = []

        # Write template
        tmpl = self.jinja_env.get_template(self.template)
        fp_out.write(tmpl.render(mainMap_content=mainMap_content,
                                 refMap_content=refMap_content,
                                 color_list=color_list,
                                 boundaries=boundaries,
                                 **self.navigator_options))

    def html(self, url):
        return '<embed src="%s" type="%s" width="%d" height="%d"/>' % \
               (url, self.mime_type, self.navigator_options['image_view'][0],
                self.navigator_options['image_view'][1])


IMAGE_PROCESSORS =  [SVGNavigatorOutputImage('SVG in Navigator'),
                     BasicOutputImage('png','PNG',"image/png"),
                     BasicOutputImage('jpeg','JPEG',"image/jpeg"),
                     SVGOutputImage('svg','SVG',"image/svg+xml"),
                     EPSOutputImage('eps', 'EPS'),
                     PDFOutputImage('pdf', 'PDF'),
                     ]

IMG_PROC_MAP = dict( (p.name, p) for p in IMAGE_PROCESSORS )
