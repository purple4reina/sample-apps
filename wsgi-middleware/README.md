# WSGI Application with Middleware

A very simple application that uses some wsgi middleware to turn "hello" to
"goodbye" in any response.

To run without the middleware:

```
gunicorn app:application --log-level debug
```

To run with the middleware:

```
gunicorn app:wrapped_application --log-level debug
```

Middleware example copied from [PEP
333](https://www.python.org/dev/peps/pep-0333/#middleware-components-that-play-both-sides)
then edited to transform words to my liking.
