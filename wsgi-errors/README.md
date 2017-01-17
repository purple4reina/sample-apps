# Custom WSGI App Errors

From working on https://newrelic.zendesk.com/agent/tickets/225693.

This application is to demonstrate error instrumentation when using a
non-supported or custom framework and gunicorn. (Note that results will be
different when using other wsgi servers like uwsgi or mod_wsgi)

## Starting

To start the app, just run `./start_app.sh`. This will do all you need to set
up your virtual environment and start the application with newrelic using
gunicorn. The app will be served on port 8000.

## Endpoints

The application offers 4 different endpoints to demonstrate the different ways
that errors can be handled.

1. **/okay:** This is the all healthy endpoint. You will see transactions on the
   transactions page.

2. **/unhandled:** This endpoint raises an AssertionError and does not handle it.
   You will see the apdex plummet and errors show up on the error analytics
   page.

3. **/handled:** This endpoint raises an AssertionError but handles it. The
   status is set to 500 but the wsgi application object, when called, does not
   raise an exception. In this case, you will see the apdex plummet but errors
   will _not_ show up on the error analytics page.

4. **/record\_exception:** This endpoint raises an AssertionError, handles the
   error in the same way that the _/handled_ endpoint does, but also calls
   `newrelic.agent.record_exception()`. Here too the apdex plummets, but errors
   _do_ show up on the error analytics page.

You can drive traffic to the app with this nice bash one-liner, replace `<endpoint>` with your choice from above.

```
while true ; do sleep 1 ; curl http://localhost:8000/<endpoint> ; done
```

## Code

Take a look at `app.py` for the code. Doing so is the best way to understand
what is going on in this example app.
