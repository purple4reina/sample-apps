# Streaming Contents with Flask

This app is an exploration of using iterators as part of flask apps. As a
consequence of working on [this websockets
ticket](https://newrelic.atlassian.net/browse/PYTHON-2006) it was discovered
that the `gevent-websockets` package breaks when an application returns an
iterator. The question was, then, if a flask app returns a generator, will it
too break?

The answer is no and kinda. No in that using streaming contents works as
expected. Kinda because there is no way for a view to actually be an iterator.
Instead, flask allows you to [pass generators to the Response object upon
return](http://flask.pocoo.org/docs/0.11/patterns/streaming/).


## Running

1. Set up virtual env and source it

    ```
    virtual env
    source env/bin/activate
    ```

1. Install dependencies

    ```
    pip install -r requirements.txt
    ```

1. Run the server without the agent

    ```
    python app.py
    ```

1. Run the server with the agent

    ```
    NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-python app.py
    ```
