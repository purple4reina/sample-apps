# Websockets + Gevent + Flask
*oh my...*

## What
A very helpful customer directed us to a bug with the agent and websockets. Using `flask` and `gevent-websocket`, after the initial connect, refreshing a page that uses websockets will disallow further websocket connections.

+ [Forum post](https://discuss.newrelic.com/t/bug-with-gevent-websocket/25622)
+ [Zendesk ticket](https://newrelic.zendesk.com/agent/tickets/197736)
+ [Jira ticket](https://newrelic.atlassian.net/browse/PYTHON-2006)

## Prepare
1. Start a virtual environment: `virtualenv env`
1. Source it: `source env/bin/activate`
1. Install packages: `pip install -r requirements.txt`
1. Update the `newrelic.ini` file to your liking
1. Install [Node.js](https://nodejs.org/en/download/)
1. Install websocket package for node: `npm install ws`
1. Run app: `python run.py`

## Enjoy
This application provides you with three enjoyable ways to provide you with endless entertainment. Two of them are accessed using a browser, the third uses a node.js script.

**http: //localhost:9191/**: Using a browser, this page will display the sample given by our customer in his [forum post](https://discuss.newrelic.com/t/bug-with-gevent-websocket/25622). The page will open a websocket to `/chat/` and display to you the status of the connection (connected or disconnected). Before the bug fix in [PYTHON-2006](https://newrelic.atlassian.net/browse/PYTHON-2006), the page was unable to maintain an open websocket connection after the page was refreshed.

**http: //localhost:9191/index/**: Using a browser, this page will simply display "Hello World". Not very exciting aye?

**Node script**: Running `node websocket_connect.js ws://localhost:9191/index/` connects to the same endpoint as above but does so with a websocket. In the terminal of both the run server and the script, messages will be logged indicating that the connection is active.
