import newrelic.agent
newrelic.agent.initialize('newrelic.ini')


def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'*']


newrelic.agent.wrap_wsgi_application(__name__, 'application')
