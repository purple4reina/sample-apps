import atexit

try:
    # PY3
    from http.client import HTTPSConnection
except ImportError:
    # PY2
    from httplib import HTTPSConnection


def myatexit():
    HTTPSConnection('https://example.com', port=443)


def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'*']


atexit.register(myatexit)
