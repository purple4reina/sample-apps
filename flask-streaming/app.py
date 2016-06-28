from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from middleware import HelloGoodbyer
from testingtools import printcolor as pc
import flask
import newrelic.agent

app = flask.Flask(__name__)
class DoNotEnter(Exception): pass


def countdown_iter(count):
    yield '<html><head><title>count</title></head><body>'
    while count:
        count -= 1
        yield '<div>%s</div>' % count
    yield '</body></html>'


@app.route('/')
def long_list():
    pc.print_blue('/')
    ws = flask.request.environ.get('wsgi.websocket')
    if not ws:
        raise DoNotEnter('Go away, this is only for websockets!')
    pc.print_green('sending message...')
    ws.send('%sHello WebSocket!%s' % (pc.colors.GREEN, pc.colors.COLOR_OFF))
    return flask.Response(countdown_iter(10))


# Wrap the application in middleware
wrapped_app = HelloGoodbyer(app)


if __name__ == '__main__':
    pc.print_red('Starting agent...')
    newrelic.agent.initialize(config_file='newrelic.ini')
    pc.print_red('Initializing agent...')
    newrelic.agent.register_application()

    pc.print_red('Starting server...')
    WSGIServer(
        ('0.0.0.0', 5000),
        wrapped_app,  # use middleware
        #app,
        handler_class=WebSocketHandler,
    ).serve_forever()
