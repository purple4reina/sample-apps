from cheroot import wsgi


def app(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type','text/plain')]
    start_response(status, response_headers)
    return ['*']


if __name__ == '__main__':
    addr = '0.0.0.0', 8080
    server = wsgi.Server(addr, app)
    server.start()
