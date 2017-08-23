"""Sets up global jinja2 environment for processing templates."""
import jinja2
import urlparse
try:
    import json
except ImportError:
    import simplejson as json

_JINJA_ENV = None

@jinja2.contextfilter
def _abspath(cntx, value):
    conf = cntx['conf']
    return urlparse.urljoin(conf.site_url, value)

def _jsonencode(value):
    return json.dumps(value)

def get_jinja_env(conf=None):
    """Get the global jinja environment.

    Environment global 'conf' is updated with conf.
    """
    global _JINJA_ENV
    if _JINJA_ENV is None:
        loader = jinja2.PackageLoader('qmbpmn.web') 
        _JINJA_ENV = jinja2.Environment(loader=loader)
        _JINJA_ENV.filters['jsonencode'] = _jsonencode
        _JINJA_ENV.filters['abspath'] = _abspath
    if conf:
        _JINJA_ENV.globals['conf'] = conf
    return _JINJA_ENV
