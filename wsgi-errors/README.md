# Custom WSGI App Errors

From working on https://newrelic.zendesk.com/agent/tickets/225693.

This application is to demonstrate error instrumentation when using a
non-supported or custom framework and gunicorn. (Note that results will be
different when using other wsgi servers like uwsgi or mod_wsgi)

## Starting

To start the app, just run `./start_app.sh gunicorn` or `./start_app.sh uwsgi`.
This will do all you need to set up your virtual environment and start the
application with newrelic using gunicorn or uwsgi. The app will be served on
port 8000.

## Endpoints

The application offers 4 different endpoints to demonstrate the different ways
that errors can be handled.

1. **/okay:** This is the all healthy endpoint.

2. **/unhandled:** This endpoint raises an AssertionError and does not handle it.

3. **/handled:** This endpoint raises an AssertionError but handles it. The
   status is set to 500 but the wsgi application object, when called, does not
   raise an exception.

4. **/record\_exception:** This endpoint raises an AssertionError, handles the
   error in the same way that the _/handled_ endpoint does, but also calls
   `newrelic.agent.record_exception()`.

You can drive traffic to the app with this nice bash one-liner, replace `<endpoint>` with your choice from above.

```
while true ; do sleep 1 ; curl http://localhost:8000/<endpoint> ; done
```

## Code

Take a look at `app.py` for the code. Doing so is the best way to understand
what is going on in this example app. Notice the two newrelic specific bits of
code that are added, `newrelic.agent.record_exception` and
`@newrelic.agent.wsgi_application`.

## WSGI Server Comparisons

The agent acts differently based on the wsgi server being used. Here are some
comparisons.

### Gunicorn

|Endpoint|Transaction Traces|Apdex|Error Analytics|
|-----|-----|-----|-----|
|**/okay**|Yes|Good|n/a|
|**/unhandled**|Yes|Bad|Yes|
|**/handled**|Yes|Bad|No|
|**/record\_exception**|Yes|Bad|Yes|

### uWSGI w/o `@newrelic.agent.wsgi_application` wrapper

|Endpoint|Transaction Traces|Apdex|Error Analytics|
|-----|-----|-----|-----|
|**/okay**|No|None|n/a|
|**/unhandled**|No|None|No|
|**/handled**|No|None|No|
|**/record\_exception**|No|None|No|

### uWSGI w/ `@newrelic.agent.wsgi_application` wrapper

|Endpoint|Transaction Traces|Apdex|Error Analytics|
|-----|-----|-----|-----|
|**/okay**|Yes|Good|n/a|
|**/unhandled**|Yes|Bad|Yes|
|**/handled**|Yes|Bad|No|
|**/record\_exception**|Yes|Bad|Yes|
