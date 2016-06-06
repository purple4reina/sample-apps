#!/usr/bin/env python

import datetime
import time


def sleepy(environ, start_response):
    print '--------------------starting--------------------'
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]

    # Each request will sleep for 1 second.
    time.sleep(10)

    timestamp = str(datetime.datetime.now())

    start_response(status, response_headers)
    print 'status: ', status
    print 'timestamp: ', timestamp
    return ['The time is now: ', timestamp]
