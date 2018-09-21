import atexit
import requests


def myatexit():
    requests.get('https://example.com')


def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'*']


atexit.register(myatexit)
