import newrelic.agent


def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [str(environ)]


application = newrelic.agent.WSGIApplicationWrapper(application)
