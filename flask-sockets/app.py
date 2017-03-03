import time

from flask import Flask
from flask_sockets import Sockets

from newrelic.agent import background_task

app = Flask(__name__)
sockets = Sockets(app)

@sockets.route('/echo')
def echo_socket(ws):
    message = 'Hello!'
    for _ in xrange(10):
        if ws.closed:
            break
        ws.send(message)
        message = ws.receive()
        time.sleep(0.5)
    print 'exiting...'

if __name__ == "__main__":
    from gevent import pywsgi
    from geventwebsocket.handler import WebSocketHandler
    server = pywsgi.WSGIServer(('', 5000), app, handler_class=WebSocketHandler)
    server.serve_forever()
