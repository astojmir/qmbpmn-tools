#! {{ conf.python_bin }} -u

import sys, cgi
cgi.maxlen = 1 << 21
{%- if conf.debug %}
import cgitb; cgitb.enable()
{%- endif %}

sys.path.insert(0, '{{- conf.python_modules_dir -}}')
{% for path in conf.python_paths -%}
sys.path.insert(0, '{{- path -}}')
{%- endfor %}

from qmbpmn.web.conf import QMBPMNSiteConf
conf = QMBPMNSiteConf('{{- conf_path -}}', True)
from qmbpmn.web.ITMProbe.runs import VIEWS as views_map
{%- if conf.debug %}
from qmbpmn.web.view_wrappers import cgi_response_web_debug as response
{%- else %}
from qmbpmn.web.view_wrappers import cgi_response_production as response
{%- endif %}

try:
    cgi_field = cgi.FieldStorage()
    conf.error_template = 'ITMProbe/error.html'
except ValueError, e:
    cgi_field = None

response(views_map, cgi_field, conf)


