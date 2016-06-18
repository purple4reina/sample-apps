#!/usr/bin/env python2.7

# pip install  newrelic    gevent  gevent-websocket flask
# my versions: (2.50.0.39) (1.0.2) (0.9.3)          (0.10.1)
from flask import Flask, request
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from testingtools import printcolor as pcolor
import newrelic.agent

# Flask app
app = Flask(__name__)


@app.route('/')
def index():
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
    <p>
        Connected right? Click Refresh (closes the first websocket) and it's
        unable to connect. Restarting the server is required to connect again.
    </p>
    <script type="text/javascript">
        $(function() {
            var ws = new WebSocket("ws://localhost:9191/chat/");
            ws.onmessage = function(evt) {
                $("#placeholder").append('<p>' + evt.data + '</p>');
            };
            ws.onopen = function(evt) {
                $('#conn_status').html('<b>Connected</b>');
            };
            ws.onerror = function(evt) {
                $('#conn_status').html('<b>Error</b>');
            };
            ws.onclose = function(evt) {
                $('#conn_status').html('<b>Closed</b>');
            };
        });
    </script>
</body>
</html>
"""


@app.route('/chat/')
def api():
    pcolor.print_blue('/chat/ ...')
    if request.environ.get('wsgi.websocket'):
        pcolor.print_green('Websocket received...')
        websocket = request.environ['wsgi.websocket']
        while True:
            message = websocket.receive()
            websocket.send(message)
    return ''


if __name__ == '__main__':
    pcolor.print_red('Starting agent...')
    newrelic.agent.initialize(config_file='newrelic.ini')

    pcolor.print_red('Running app...')
    WSGIServer(
        ('0.0.0.0', 9191),
        app,
        handler_class=WebSocketHandler,
    ).serve_forever()
