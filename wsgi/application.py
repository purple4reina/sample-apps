import newrelic.agent
newrelic.agent.initialize('newrelic.ini')

class Application(object):
    def application(self, environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]
        start_response(status, response_headers)
        return [b'Hello World']

newrelic.agent.wrap_wsgi_application(__name__, 'Application.application')
