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
WITH_AGENT                          = False
WITH_FIXED_GEVENT_WEBSOCKET_PACKAGE = True
WITH_RUM_MIDDLEWARE                 = False
WITH_HELLOGOODBYE_MIDDLEWARE        = True
WITH_FLASK_STREAMING                = True


def configure_testing():
    pc.print_purple('A successful test will include:')
    pc.print_purple(
        '  - Messages "sending message from view..." and '
        '"Hello back!" in terminal')
    if WITH_FIXED_GEVENT_WEBSOCKET_PACKAGE:
        os.environ['FIX_GEVENT'] = 'true'
    if WITH_RUM_MIDDLEWARE:
        os.environ['USE_RUM'] = 'true'
    if WITH_HELLOGOODBYE_MIDDLEWARE:
        pc.print_purple(
            '  - Message "changing hellos to goodbyes" in terminal')
    if WITH_FLASK_STREAMING:
        pc.print_purple(
            '  - Messages "sending message from iterator..." and '
            '"Hello back!" in terminal')


def response_iter(ws):
    # send and receive a message
    pc.print_green('sending message from iterator...')
    ws.send('%sHello from iterator!%s' % (pc.colors.GREEN, pc.colors.COLOR_OFF))
    msg = ws.receive()
    print 'message received... %s%s%s' % (pc.colors.GREEN, msg,
            pc.colors.COLOR_OFF)

    yield 'Hello World'


@app.route('/')
def long_list():
    request = flask.request
    ws = request.environ.get('wsgi.websocket')
    if not ws:
        raise DoNotEnter('Go away, this is only for websockets!')

    # send and receive a message
    pc.print_green('sending message from view...')
    ws.send('%sHello from view!%s' % (pc.colors.GREEN, pc.colors.COLOR_OFF))
    msg = ws.receive()
    print 'message received... %s%s%s' % (pc.colors.GREEN, msg,
            pc.colors.COLOR_OFF)

    if WITH_FLASK_STREAMING:
        print 'using flask streaming'
        return flask.Response(response_iter(ws), direct_passthrough=True)
    else:
        print 'not using flask streaming'
        return 'Hello World'


if __name__ == '__main__':
    if WITH_AGENT:
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
