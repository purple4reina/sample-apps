import os
import time

if os.environ.get('USE_AGENT', False):
    import newrelic.agent
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

def app_list(environ, start_response):
    time.sleep(0.5)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [PAGE_CONTENTS]

def app_iter(environ, start_response):
    time.sleep(0.5)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    yield PAGE_CONTENTS

def app_str(environ, start_response):
    time.sleep(0.5)
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return PAGE_CONTENTS
