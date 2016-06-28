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

**NOTE**: For helpful debug printing, I use my custom [testingtools](https://github.com/purple4reina/testingtools) package. You will want to download this as well. Do a `git clone git@github.com:purple4reina/testingtools.git` then make sure the directory is in your PYTHONPATH environment variable.


## Websockets

The application includes a node.js script to allow easy command line
websocket connections to the websocket endpoint. To use, you must first
download and install [Node.js](https://nodejs.org/en/download/). Then, install
the websocket package dependency with `npm install ws`.

To connect via websocket to http//localhost:5000, run `node
websocket_connect.js`.

When a connection is received at http//localhost:5000 from the node script, a message is sent from the server to the script. Once received, the script will log the message then send a message back. When the server receives this message back from the node script, it logs it then exits the view function.


## Streaming

Flask supports "streaming" views. In this case, it will return an iterator from the view and not a response object. The special kwarg `direct_passthrough=True` must be set.

We know that the iterator is executed when it communicates back and forth via the websocket with the client.


## Middleware

There is an optional `HelloGoodbyer` middleware available to the application. It exchanges the word "Hello" with "Goodbye".


## Observations

To do some quick testing, I set up 4 variables at the top of the `app.py` file. These variables are used to set up the following tests. Two are used in the `app.py` file itself, the other two required changes to exsternal packages: newrelic and gevent-websocket.

Success is defined by:
+ Websocket messages sent and received between client and server ('Hello from view!' logged by client)
+ If using Flask Streaming, websocket messages sent and received between client and server from within the `response_iter` ('Hello from iterator!' logged by client)
+ If using the `HelloGoodbyer` middleware, the server will log 'changing hellos to goodbyes' to the terminal

Where (bool,bool,bool,bool) = Fix the gevent-websocket package, use our RUM middleware, use my custom hello goodbye middleware when running the wsgi server, hit a view that uses flask streaming. Always use the agent.

1. True,True,True,True: +

1. True,True,True,False: +

1. True,True,False,True: +

1. True,True,False,False: +

1. True,False,True,True: +

1. True,False,True,False: +

1. True,False,False,True: +

1. True,False,False,False: +

1. False,True,True,True: -

1. False,True,True,False: -

1. False,True,False,True: -

1. False,True,False,False: -

1. False,False,True,True: -

1. False,False,True,False: -

1. False,False,False,True: -

1. False,False,False,False: +

Same but without the agent. (note that the second value doesn't even matter, I did it anyway just to make results easier to compare)

1. True,True,True,True: +

1. True,True,True,False: +

1. True,True,False,True: +

1. True,True,False,False: +

1. True,False,True,True: +

1. True,False,True,False: +

1. True,False,False,True: +

1. True,False,False,False: +

1. False,True,True,True: -

1. False,True,True,False: -

1. False,True,False,True: -

1. False,True,False,False: +

1. False,False,True,True: -

1. False,False,True,False: -

1. False,False,False,True: -

1. False,False,False,False: +

Based on these observations, I can come to the following conclusion: The only time that this app disallows websocket connections is when **using the buggy gevent-websocket package and any view that returns an iterator (our RUM middleware, flask streaming, `HelloGoodbyer` middleware)**. This is independent of whether it is using the agent or not.
