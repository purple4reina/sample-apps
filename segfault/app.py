import atexit
import requests
import threading


def myatexit():
    url = 'https://collector-008.newrelic.com/agent_listener/invoke_raw_method'
    params = {
        'protocol_version': '16',
        'license_key': 'f429aaa8f9c1687093c9bd211ef189b75952bf42',
        'marshal_format': 'json',
        'method': 'analytic_event_data',
        'run_id': ('WzIse2E6NDY4ODU2NDAwLGI6MTM4MzA5OTM2LGM6MTE3ODUwMCxkOiI0Lj'
                   'UuMC4wIixlOiJweXRob24iLGY6IjEzYmVjOGFjMjkyYiIsZzpbe2E6MTM4'
                   'MDM1MDY1LGI6InVXU0dJIFNlZ2ZhdWx0In1dfSwyODUxNjYzNzIwXQ'),
    }
    headers = {
        'Content-Encoding': 'identity',
        'User-Agent': 'NewRelic-PythonAgent/4.5.0.0 (Python 2.7.15 linux2)',
    }
    proxies = None
    timeout = 30.0
    data = '["WzIse2E6NDY4ODU2NDAwLGI6MTM4MzA5OTM2LGM6MTE3ODUwMCxkOiI0LjUuMC4wIixlOiJweXRob24iLGY6IjEzYmVjOGFjMjkyYiIsZzpbe2E6MTM4MDM1MDY1LGI6InVXU0dJIFNlZ2ZhdWx0In1dfSwyODUxNjYzNzIwXQ",[[{"totalTime":0.0007650852203369141,"name":"WebTransaction/Function/QWERTY","timestamp":1537555383388,"duration":0.0007650852203369141,"type":"Transaction","port":8000},{},{"response.status":"200","request.uri":"/","response.headers.contentType":"text/plain","request.method":"GET"}],[{"totalTime":0.0003581047058105469,"name":"WebTransaction/Function/QWERTY","timestamp":1537555383920,"duration":0.0003581047058105469,"type":"Transaction","port":8000},{},{"response.status":"200","request.uri":"/","response.headers.contentType":"text/plain","request.method":"GET"}],[{"totalTime":0.00029397010803222656,"name":"WebTransaction/Function/QWERTY","timestamp":1537555384450,"duration":0.00029397010803222656,"type":"Transaction","port":8000},{},{"response.status":"200","request.uri":"/","response.headers.contentType":"text/plain","request.method":"GET"}]]]'
    cert_loc = ''

    r = requests.post(url, params=params, headers=headers, proxies=proxies,
            timeout=timeout, data=data, verify=cert_loc)
    print('resp.status_code: ', resp.status_code)


def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    return [b'*']


atexit.register(myatexit)
