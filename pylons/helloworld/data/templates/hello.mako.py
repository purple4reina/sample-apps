# -*- coding:utf-8 -*-
from mako import runtime, filters, cache
UNDEFINED = runtime.UNDEFINED
STOP_RENDERING = runtime.STOP_RENDERING
__M_dict_builtin = dict
__M_locals_builtin = locals
_magic_number = 10
_modified_time = 1495483899.46279
_enable_loop = True
_template_filename = '/Users/rabolofia/Documents/sample-apps/pylons/helloworld/helloworld/templates/hello.mako'
_template_uri = '/hello.mako'
_source_encoding = 'utf-8'
from markupsafe import escape
_exports = []


def render_body(context,**pageargs):
    __M_caller = context.caller_stack._push_frame()
    try:
        __M_locals = __M_dict_builtin(pageargs=pageargs)
        __M_writer = context.writer()
        __M_writer(u'Hello World!\n')
        return ''
    finally:
        context.caller_stack._pop_frame()


"""
__M_BEGIN_METADATA
{"source_encoding": "utf-8", "line_map": {"17": 0, "28": 22, "22": 1}, "uri": "/hello.mako", "filename": "/Users/rabolofia/Documents/sample-apps/pylons/helloworld/helloworld/templates/hello.mako"}
__M_END_METADATA
"""
