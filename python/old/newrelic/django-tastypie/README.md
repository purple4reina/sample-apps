# Django TastyPie

An app that uses the TastyPie API component.

https://discuss.newrelic.com/t/python-agent-reporting-handled-exceptions-as-unhandled/50209/2

## Running the app

1. Set up a virtual env and install requirements

1. Migrate your database

    ```
    $ python manage.py migrate
    ```

1. Run the server with newrelic

    ```
    $ newrelic-admin run-python manage.py runserver
    ```

## Endpoints

There's a status endpoint at `http://localhost:8000/status/` that just returns
`OK`.

List available user objects at `http://localhost:8000/api/user/`

See details on a particular user at `http://localhost:8000/api/user/100/`, if
not found, it will return a 404.
