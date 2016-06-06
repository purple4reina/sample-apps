# WSGI Hello World

## What is WSGI?

In Python, the `Web Server Gateway Interface (WSGI)` is the standard interface between web applications and servers.

A Hello World WSGI application demonstrates that, hidden underneath all of the various Python web frameworks, a WSGI application can be quite simple:

    def application(environ, start_response):
        status = '200 OK'
        response_headers = [('Content-type', 'text/plain')]

        start_response(status, response_headers)
        return ['Hello world!']

You define a callable `WSGI application`, which can be a function, or method, or callable object. The WSGI application must accept 2 arguments: environment, and a `start_response` function. Then, it must call the `start_response` function and return a list of strings (or, an iterable of strings.)

If you'd like to read more about WSGI, [PEP 333][pep333] is the original definition of the WSGI standard, while [PEP 3333][pep3333] provides a few updates.

[pep333]: https://www.python.org/dev/peps/pep-0333/
[pep3333]: https://www.python.org/dev/peps/pep-3333/

## Purpose of Repository

This repo shows how to run this Hello World app using the 3 most popular WSGI servers:

1. gunicorn
2. uwsgi
3. mod_wsgi

Also, included are examples of how to run the app using `gevent` workers, how to use the `newrelic-admin` wrapper script, and how to do manual integration of the agent.

Once it's clear how to run a Hello World application, the hope is that it will be equally clear how to run any WSGI application, by first identifying where the `WSGI application` is defined, and then starting up the WSGI server.

## Install

To install the different WSGI servers, run this command (preferably inside of a virtualenv):

    $ pip install -r requirements.txt

## Run application

### gunicorn

    $ gunicorn app

    $ gunicorn app:application

### uwsgi

    $ uwsgi --http :8000 --wsgi-file app.py

    $ uwsgi --http :8000 --wsgi app:application

### mod_wsgi

    $ mod_wsgi-express start-server app.py

    $ mod_wsgi-express start-server --application-type module app

    $ mod_wsgi-express start-server \
        --application-type module app \
        --callable-object application

## Run application with gevent

The `sleepy` application will pause for 1 second, then print out the current time.

If `sleepy` is run with a blocking WSGI server, 2 concurrent requests will take a total of 2 seconds to complete. If `sleepy` is run with `gevent`, then 2 concurrent requests will take a total of 1 seconds, because `time.sleep()` will have been monkeypatched by `gevent` to become non-blocking.

### gunicorn

    $ gunicorn --worker-class gevent sleep:sleepy

### uwsgi

    $ uwsgi --http :8000 --gevent 100 --wsgi sleep:sleepy

### mod_wsgi

It's not possible to run mod_wsgi with gevent workers.


## Run application with New Relic wrapper script

### gunicorn

    $ newrelic-admin run-program gunicorn app:application

### uwsgi

    $ newrelic-admin run-program uwsgi \
        --http :8000 \
        --wsgi-file app.py \
        --single-interpreter \
        --enable-threads

### mod_wsgi

    $ mod_wsgi-express start-server app.py --with-newrelic

## Run application with manual integration of New Relic agent

### gunicorn

    $ gunicorn manual_app:application

### uwsgi

    $ uwsgi \
        --http :8000 \
        --wsgi manual_app:application \
        --single-interpreter \
        --enable-threads

### mod_wsgi

    $ mod_wsgi-express start-server manual_app.py

