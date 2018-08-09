# uWSGI with PyPY

https://newrelic.zendesk.com/agent/tickets/308760

This application demonstrates a bug in uwsgi's pypy implementation that raises
the following error:

```
From cffi callback <function uwsgi_pypy_wsgi_handler at 0x00007f144c981178>:
Traceback (most recent call last):
  File "c callback", line 472, in uwsgi_pypy_wsgi_handler
  File "./app.py", line 16, in __call__
    for item in self.application(environ, start_response):
TypeError: iter() returned non-iterator
```

This is happening because uwsgi's WSGIfilewrapper is not an iterable.

## To reproduce

```bash
docker run -it -v $PWD:/data -p 8000:8000 --network="bridge" cache bash
cd data
source /venvs/pypy/bin/activate
pip install uwsgi==2.0.17.1
uwsgi --ini uwsgi.ini
```

Then go to `http://192.168.99.100:8000/` in your browser (possibly replacing
the IP with the value from $DOCKER_HOST)

Alternatively, you can `docker exec` into the container and use curl.

## To fix

To fix the crash, uncomment this line from the `uwsgi.ini` file:

```
pypy-setup = pypy_setup.py
```

This will force uwsgi to use the fixed version of the WSGIfilewrapper.
