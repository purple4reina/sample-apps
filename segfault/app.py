import atexit
import requests


def myatexit():
    resp = requests.get('https://example.com')
    print('resp.status_code: ', resp.status_code)


def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'*']


atexit.register(myatexit)
