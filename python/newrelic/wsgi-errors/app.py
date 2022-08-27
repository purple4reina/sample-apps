import newrelic.agent

@newrelic.agent.wsgi_application()
def application(environ, start_response):
    path = environ.get('PATH_INFO')
    method = environ.get('REQUEST_METHOD')

    # 1) Unhandled exception
    if path == '/unhandled':
        assert False

    # 2) Handled exception
    elif path == '/handled':
        try:
            assert False
        except AssertionError as e:
            status = '500'

    # 3) Record exception
    elif path == '/record_exception':
        try:
            assert False
        except AssertionError as e:
            status = '500'
            newrelic.agent.record_exception()

    # 4) Okay, no errors
    else:
        status = '200 OK'

    response_headers = [('Content-type', 'text/plain')]
    start_response(status, response_headers)
    print '[%s]: "%s", status: %s' % (method, path, status)
    return [b'*']
