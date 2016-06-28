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

1. View the page at http://localhost:5000


## Websockets

To hit the endpoint with a websocket using the commandline use curl:

```
curl -i -H "Connection: Upgrade" \
    -H "Upgrade: websocket" \
    -H "Host: localhost:5000" \
    -H "Origin:http://localhost:5000" \
    -H "Sec-WebSocket-Version: 13" \
    -H "Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==" \
    http://localhost:5000
```

Notice that when running the developement server using `python app.py` it
returns an empty reply. However, try running the server with the agent thus:

```
FLASK_APP=app FLASK_DEBUG=1 NEW_RELIC_CONFIG_FILE=newrelic.ini newrelic-admin run-program flask run
```

Then hit it again with the curl command. It will return the contents of the
page as expected, including the RUM. No errors. However, it is not using
`gevent-websocket`.
