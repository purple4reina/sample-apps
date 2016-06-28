import os
from gevent.pywsgi import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from middleware import HelloGoodbyer
from testingtools import printcolor as pc
import flask
import newrelic.agent

app = flask.Flask(__name__)
wrapped_app = HelloGoodbyer(app)
class DoNotEnter(Exception): pass


# for testing, define here what features to enable/disable
WITH_FIXED_GEVENT_WEBSOCKET_PACKAGE = True
WITH_RUM_MIDDLEWARE                 = True
WITH_HELLOGOODBYE_MIDDLEWARE        = True
WITH_FLASK_STREAMING                = True


def configure_testing():
    if WITH_RUM_MIDDLEWARE:
        os.environ['USE_RUM'] = 'true'
    if WITH_FIXED_GEVENT_WEBSOCKET_PACKAGE:
        os.environ['FIX_GEVENT'] = 'true'


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

    # send and receive a message
    pc.print_green('sending message...')
    ws.send('%sHello WebSocket!%s' % (pc.colors.GREEN, pc.colors.COLOR_OFF))
    msg = ws.receive()
    print 'message received... %s%s%s' % (pc.colors.GREEN, msg,
            pc.colors.COLOR_OFF)

    if WITH_FLASK_STREAMING:
        print 'using flask streaming'
        return flask.Response(countdown_iter(10))
    else:
        print 'not using flask streaming'
        return 'Hello World'


if __name__ == '__main__':
    pc.print_red('Starting agent...')
    newrelic.agent.initialize(config_file='newrelic.ini')
    pc.print_red('Initializing agent...')
    newrelic.agent.register_application()

    # configure for testing
    runapp = wrapped_app if WITH_HELLOGOODBYE_MIDDLEWARE else app
    print 'using hello goodbye middleware: ', WITH_HELLOGOODBYE_MIDDLEWARE
    configure_testing()

    pc.print_red('Starting server...')
    WSGIServer(
        ('0.0.0.0', 5000),
        runapp,
        handler_class=WebSocketHandler,
    ).serve_forever()
