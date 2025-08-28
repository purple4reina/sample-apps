import time

from opentelemetry import trace

tracer = trace.get_tracer(__name__)

def app(environ, start_response):
    with tracer.start_as_current_span('my-function'):
        data = b'ok'
        status = '200 OK'
        response_headers = [
            ('Content-type', 'text/plain'),
            ('Content-Length', str(len(data)))
        ]
        with tracer.start_as_current_span('start_response'):
            start_response(status, response_headers)
        return iter([data])
