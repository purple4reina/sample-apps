#!/usr/bin/env python

import newrelic.agent
import time
newrelic.agent.initialize('newrelic.ini')

@newrelic.agent.wsgi_application()
def application(environ, start_response):
    print '--------------------start--------------------'
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]

    time.sleep(10)

    start_response(status, response_headers)
    return ['Hello world!']
