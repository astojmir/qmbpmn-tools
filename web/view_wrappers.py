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

import sys
from . import exceptions as exc
from .response import html_response
from ..common.utils.jinjaenv import get_jinja_env
from . import validators as vld


# *** Must import conf into the global jinja_env before doing anything else ***

def map_cgi_field(cgi_field):

    if cgi_field == None:
        raise exc.TooLargeFile()
    cgi_map = dict( (k, cgi_field.getfirst(k)) for k in cgi_field.keys() )
    return cgi_map


def error_view(jinja_env, conf, e):

    tmpl = jinja_env.get_template(conf.error_template)
    data = tmpl.render(error_msg=e.__str__())
    html_response(data)

def view_dispatcher(cgi_map, conf, views_map):

    view_func, _ = vld.find_input_option(cgi_map, 'view', views_map)
    view_func(cgi_map, conf)


def cgi_response_web_debug(views_map, cgi_field, conf):

    jinja_env = get_jinja_env(conf)
    cgi_map = map_cgi_field(cgi_field)
    view_dispatcher(cgi_map, conf, views_map)

def cgi_response_production(views_map, cgi_field, conf):

    jinja_env = get_jinja_env(conf)
    try:
        cgi_map = map_cgi_field(cgi_field)
        view_dispatcher(cgi_map, conf, views_map)
    except exc.WebException, e:
        error_view(jinja_env, conf, e)
    except:
        e = exc.WebException()
        error_view(jinja_env, conf, e)
