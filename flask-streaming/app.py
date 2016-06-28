import flask
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler

app = flask.Flask(__name__)


def countdown_iter(count):
    yield '<html><head><title>count</title></head><body>'
    while count:
        count -= 1
        yield '<div>%s</div>' % count
    yield '</body></html>'


@app.route('/')
def long_list():
    return flask.Response(countdown_iter(10))


if __name__ == '__main__':
    WSGIServer(
        ('0.0.0.0', 5000),
        app,
        handler_class=WebSocketHandler,
    ).serve_forever()
