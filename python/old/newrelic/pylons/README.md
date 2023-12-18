# Pylons

To start app:

```
cd helloworld
newrelic-admin run-program paster serve --reload development.ini
```

The endpoints are:

1. `/` -- Pylons hello splash page
2. `/hello/index` -- Returns `Hello World!` using a mako template
3. `/cats/index` -- Returns `Hello Cats!` not using a template

Served to port 5000
