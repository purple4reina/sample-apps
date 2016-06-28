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

1. Run the server with the agent

    ```
    python app.py
    ```


## Websockets

The application includes a node.js script to allow easy command line
websocket connections to the websocket endpoint. To use, you must first
download and install [Node.js](https://nodejs.org/en/download/). Then, install
the websocket package dependency with `npm install ws`.

To connect via websocket to http//localhost:5000, run `node
websocket_connect.js`.


## Middleware

There is an optional middleware available to the application. It exchanges the word "Hello" with "Goodbye".

## Observations
