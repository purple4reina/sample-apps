from testingtools import printcolor as pcolor
import newrelic.agent
pcolor.print_red('Starting agent...')
newrelic.agent.initialize(config_file='newrelic.ini')
pcolor.print_red('Initializing agent...')
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


def simple():
    return 'hello world'


@app.route('/')
def index():
    pcolor.print_blue('/')
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
    try:
        pcolor.print_blue('/chat/ ...')
        if request.environ.get('wsgi.websocket'):
            websocket = request.environ['wsgi.websocket']
            while True:
                pcolor.print_green('waiting for message')
                message = websocket.receive()
                pcolor.print_green('message received! {}'.format(message))
                websocket.send('sending message')
                pcolor.print_green('message sent!')
        else:
            pcolor.print_purple('not a websocket')
    except Exception as e:
        pcolor.print_red('oooops! error! {}'.format(e))
    return 'Hello World'


@app.route('/socket/')
def socket():
    # just a websocket endpoint, sends messages back every second
    pcolor.print_blue('/socket/ ...')
    try:
        ws = request.environ.get('wsgi.websocket')
        if ws:
            while True:
                now = int(str(int(time.time()))[-5:])
                pcolor.print_green('sending message {} ...'.format(now))
                ws.send('{}Here is a message! {}{}\n'.format(
                    colors.GREEN, now, colors.COLOR_OFF))
                time.sleep(1)
        else:
            pcolor.print_purple('not a websocket request')
    except Exception as e:
        pcolor.print_red('ooops! {}'.format(e))
    return 'Hello World!'


@app.route('/index/')
def both():
    ws = request.environ.get('wsgi.websocket')
    pcolor.print_yellow('/index/...')
    if ws:
        try:
            cnt = 1
            while True:
                cnt += 1
                pcolor.print_green('sending message {} ...'.format(cnt))
                ws.send('{}Here is a message! {}{}\n'.format(
                    colors.GREEN, cnt, colors.COLOR_OFF))
                time.sleep(1)
        except WebSocketError:
            pass
    return 'Hello World'


@app.route('/http/')
def just_an_http_point():
    pcolor.print_blue('/http/...')
    cnt = 30
    while cnt >= 0:
        pcolor.print_green(cnt)
        time.sleep(1)
        cnt -= 1
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

    pcolor.print_red('Running app... on port {}'.format(port))
    WSGIServer(
        ('0.0.0.0', port),
        app,
        handler_class=WebSocketHandler,
    ).serve_forever()
