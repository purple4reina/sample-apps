import os
import time
import newrelic.agent

if os.environ.get('USE_AGENT', False):
    newrelic.agent.initialize('newrelic.ini')
    newrelic.agent.register_application(timeout=10.0)

PAGE_CONTENTS = """
<html>
    <head>
        <meta charset="utf-8">
        <title>Title</title>
    </head>
    <body>
        Hello World
    </body>
</html>
"""

GIT_SHA = os.environ.get('GIT_SHA', 'Root path')

def app_list(environ, start_response):
    newrelic.agent.set_transaction_name(GIT_SHA)
    time.sleep(0.5)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [PAGE_CONTENTS]

def app_iter(environ, start_response):
    newrelic.agent.set_transaction_name(GIT_SHA)
    time.sleep(0.5)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    yield PAGE_CONTENTS

def app_str(environ, start_response):
    newrelic.agent.set_transaction_name(GIT_SHA)
    time.sleep(0.5)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return PAGE_CONTENTS

def app_list_exc_1(environ, start_response):
    newrelic.agent.set_transaction_name(GIT_SHA)
    time.sleep(0.5)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    1/0
    return [PAGE_CONTENTS]

def app_list_exc_2(environ, start_response):
    newrelic.agent.set_transaction_name(GIT_SHA)
    time.sleep(0.5)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    1/0
    start_response(status, response_headers)
    return [PAGE_CONTENTS]

def app_iter_exc_1(environ, start_response):
    newrelic.agent.set_transaction_name(GIT_SHA)
    time.sleep(0.5)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    1/0
    yield PAGE_CONTENTS
