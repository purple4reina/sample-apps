#!/usr/bin/env python

import random
import time


def application(environ, start_response):
    print '--------------------application--------------------'
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]

    time.sleep(10)

    start_response(status, response_headers)
    return ['Hello world! %s' % random.randrange(100, 200)]
