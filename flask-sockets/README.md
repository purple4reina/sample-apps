# Flask Sockets

https://newrelic.zendesk.com/agent/tickets/232717

## Setup

1. Create a virtualenv: `virtualenv env`
1. Activate it: `source env/bin/activate`
1. Install stuffs: `pip install -r requirements.txt`
1. Start the server: `newrelic-admin run-program python app.py`

## Enjoy

1. Install [Node.js](https://nodejs.org/en/download/)
1. Install websocket package for node: `npm install ws`
1. Connect to the app with a websocket: `node websocket_connect.js ws://localhost:5000/echo`

## Details

1. No transactions are created, this is because we ignore websockets
1. We _might_ be able to record something by adding the
   `@newrelic.agent.background_task()` decorator to the view, but I haven't
   been able to get it working yet
