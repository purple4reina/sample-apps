try:
    from testingtools.printcolor import (
        print_red, print_blue, print_green, print_purple, print_yellow,
    )
except ImportError:
    def _print(text):
        print text
    print_red = _print
    print_blue = _print
    print_green = _print
    print_purple = _print
    print_yellow = _print

import newrelic.agent
print_red('Starting agent...')
newrelic.agent.initialize(config_file='newrelic.ini')
print_red('Initializing agent...')
newrelic.agent.register_application()

from flask import Flask, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.exceptions import WebSocketError
from geventwebsocket.handler import WebSocketHandler
from testingtools import colors
import sys
import time

# Flask app
app = Flask(__name__)


@app.route('/')
def home():
    # the original html given in the forum post
    print_blue('/')
    return """
<!DOCTYPE HTML>
<html>
<head>
    <title>WebSocket Failure</title>
    <script type="text/javascript" src="http://code.jquery.com/jquery-1.4.2.min.js">
    </script>
</head>
<body>
    <h1>WebSocket Failure</h1>
    <div id="conn_status">Not Connected</div>
    <p><button onclick="location.reload()">Reload</button></p>
    <script type="text/javascript">
        $(function() {
            var ws = new WebSocket("ws://localhost:9191/chat/");
            console.log(ws);
            ws.onmessage = function(evt) {
                console.log("onmessage");
                $("#placeholder").append('<p>' + evt.data + '</p>');
            };
            ws.onopen = function(evt) {
                console.log("onopen");
                ws.send('<html><body>send something down the pipe</body></html>');
                $('#conn_status').html('<b>Connected</b>');
            };
            ws.onerror = function(evt) {
                console.log("onerror");
                $('#conn_status').html('<b>Error</b>');
            };
            ws.onclose = function(evt) {
                console.log("onclose");
                $('#conn_status').html('<b>Closed</b>');
            };
        });
    </script>
</body>
</html>
"""

@app.route('/chat/')
def api():
    # The endpoint the above html will connect to with a websocket
    try:
        print_blue('/chat/ ...')
        if request.environ.get('wsgi.websocket'):
            websocket = request.environ['wsgi.websocket']
            while True:
                print_green('waiting for message')
                message = websocket.receive()
                print_green('message received! {}'.format(message))
                websocket.send('sending message')
                print_green('message sent!')
        else:
            print_purple('not a websocket')
    except Exception as e:
        print_red('oooops! error! {}'.format(e))
    return 'Hello World'


@app.route('/index/')
def index():
    # An endpoint that can accept either websocket or http requests
    print_blue('/index/...')

    ws = request.environ.get('wsgi.websocket')
    print_blue('...websocket' if ws else '...not websocket')

    if ws:
        try:
            cnt = 1
            while True:
                cnt += 1
                print_green('sending message {} ...'.format(cnt))
                ws.send('Here is a message! {}'.format(cnt))
                time.sleep(1)
        except WebSocketError:
            pass
    return 'Hello World'


if __name__ == '__main__':

    try:
        port = sys.argv[1]
        port = int(port)
    except IndexError:
        port = 9191
    except ValueError:
        print 'Give me an integer please!'
        sys.exit(1)

    print_red('Running app... on port {}'.format(port))
    WSGIServer(
        ('0.0.0.0', port),
        app,
        handler_class=WebSocketHandler,
    ).serve_forever()
