#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import cherrypy
import functools
import json
import boto3
import requests
from cherrypy import HTTPError, HTTPRedirect, InternalRedirect

import newrelic.agent

import moto


"""API Decorator"""
# Prepare decorator to accept multiple parameters
decorator_with_args = lambda decorator: lambda *args, **kwargs: lambda func: decorator(func, *args, **kwargs)

@decorator_with_args
def api(func, s=True, p=False):
    """Decorator for cherrypy expose, security, JSON econding and pasthru (s=sec, a=alias, p=Passthru)"""

    @functools.wraps(func)
    def SDPYD(request, *args, **kwargs):
        """The inner returned function"""

        # Set headers
        cherrypy.response.headers['Server'] = "PiniOn"

        # Synthesize the response
        res = func(request, *args, **kwargs)

        # Passthru
        if p:
            return res

        cherrypy.response.headers['Content-Type'] = 'application/json'

        return json.dumps(res).encode('utf8')


    SDPYD.__name__ = func.__name__
    SDPYD.__doc__ = func.__doc__
    SDPYD.__dict__ = func.__dict__
    # Exposes to cherrypy dispatcher
    SDPYD.exposed = True

    return SDPYD


class Root:

    def __init__(self):

        """Amazon S3 Init"""
        self.s3 = boto3.client(
            service_name            = "s3",
            region_name             = "sa-east-1",
            aws_access_key_id       = "---------",
            aws_secret_access_key   = "---------"
        )

    @api(p=True, s=False)
    def default(self, *args, **kwargs):
        """API Info"""

        nfo = """
        <form action="/bototest" method="post" enctype="multipart/form-data">
            <input type="file" name="archive" />
            <br>
            <input type="submit" />
        </form>
        """

        return nfo

    @moto.mock_s3
    @api()
    def bototest(self, *args, **kwargs):
        """
            This is the test method.
            File should be on kwargs[archive]
        """
        try:
            self.s3.create_bucket(Bucket='mytestbucket')
            with open('empty') as f:
                fup = self.s3.upload_fileobj(
                    Bucket = 'mytestbucket',
                    Key = 'mytestkey', #"nrtests/%s" % kwargs.get("archive").filename,
                    Fileobj = f, #kwargs.get("archive").file,
                    #ExtraArgs = {
                    #    "ACL": "public-read"
                    #}
                )
        except Exception as e:
            print('e: ', e)
            #raise


def handle_error():
    """Unanticipated Error Handler"""
    print('--------------------error--------------------')

    cherrypy.response.status = 500
    cherrypy.response.body = [e.encode() for e in [
        #"GLOBALEXCEPTIIONCATCHER",
        #"<br/>",
        #"DEBUG: %s" % debug.inserted_id
        '*'
    ]]

def error_page(status, message, traceback, version):
    """Renders default error page"""

    return "%s" % message

if __name__ == "__main__":
    # Local Developer Mode
    newrelic.agent.initialize('../newrelic.ini')

    cherrypy.quickstart(Root(), '/', config={
        'global': {
            'server.environment': 'development',
            'engine.autoreload.on': True,
            'server.socket_host': '0.0.0.0',
            'server.socket_port': 8080,
            'tools.trailing_slash.on': False,
            'tools.trailing_slash.missing': False,
            'tools.trailing_slash.extra': False,
            'log.screen': True,
            'error_page.default': error_page,
            'request.error_response': handle_error
        },
        '/': {
            'request.show_tracebacks': True,
            'tools.decode.on':True,
            'tools.decode.default_encoding':'utf-8',
            'tools.encode.on':True,
            'tools.encode.encoding':'utf-8',
            'tools.encode.errors':'replace',
            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/*', 'application/json'],
            'error_page.default': error_page,
            'request.error_response': handle_error
        }
    })
else:
    # Production Mode

    # Check for Prod Dev Mode (For dev servers)
    if conf.get("env") == "dev":
        dev = True
    else:
        dev = False
        newrelic.agent.initialize('/opt/api/current/s/newrelic.ini')

    application = cherrypy.tree.mount(Root(), '', config={
        'global': {
            'server.environment': 'development' if dev else 'production',
            'tools.trailing_slash.on': False,
            'tools.trailing_slash.missing': False,
            'tools.trailing_slash.extra': False,
            'log.screen': True,
            'error_page.default': error_page,
            'request.error_response': handle_error
        },
        '/': {
            'request.show_tracebacks': True,
            'tools.decode.on':True,
            'tools.decode.default_encoding':'utf-8',
            'tools.encode.on':True,
            'tools.encode.encoding':'utf-8',
            'tools.encode.errors':'replace',
            'tools.gzip.on': True,
            'tools.gzip.mime_types': ['text/*', 'application/json'],
            'error_page.default': error_page,
            'request.error_response': handle_error
        }
    })
