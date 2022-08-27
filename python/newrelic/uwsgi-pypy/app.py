def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)

    file_wrapper = environ.get('wsgi.file_wrapper')
    return file_wrapper(open('hello_world.txt'), 1)


class ConsumingMiddleware(object):
    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        data = []
        for item in self.application(environ, start_response):
            data.append(item + '?')
        return data


application = ConsumingMiddleware(application)
