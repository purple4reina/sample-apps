import time
from testingtools import printcolor as pcolor

import newrelic.agent

import tornado.ioloop
import tornado.web
import tornado.options
import tornado.websocket


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('Hello World')


class SlowHandler(tornado.web.RequestHandler):
    def get(self):
        pcolor.print_blue('/slow/...')
        cnt = 30
        while cnt:
            cnt -= 1
            pcolor.print_blue('Sl%sw' % ('o' * cnt))
            time.sleep(1)
        self.write('Slow World')


class ErrorHandler(tornado.web.RequestHandler):
    def get(self):
        raise Exception('oooops!')


class WebSocketHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        pcolor.print_blue('websocket opened...')
        self.write_message('Hello WebSocket')
        self.close()

    def on_close(self):
        pcolor.print_blue('websocket closed')

    def write_message(self, msg):
        rtn = super(WebSocketHandler, self).write_message(msg)
        pcolor.print_yellow('Sending message... %s' % msg)
        return rtn


class AsyncHandler(tornado.web.RequestHandler):

    def get(self):
        pcolor.print_blue('/async/...')
        self.write('Hello World')
        self.finish()
        self.sleep_some(10)

    def sleep_some(self, sec):
        time.sleep(sec)
        pcolor.print_yellow('async done sleeping')


def make_app():
    return tornado.web.Application(
        [
            (r'/', MainHandler),
            (r'/slow/', SlowHandler),
            (r'/error/', ErrorHandler),
            (r'/socket/', WebSocketHandler),
            (r'/async/', AsyncHandler),
        ],
        debug=True,
    )


if __name__ == '__main__':
    # sets up debugging to stdout
    tornado.options.parse_command_line()

    # start agent
    newrelic.agent.initialize(config_file='newrelic.ini')
    # initialize
    newrelic.agent.register_application()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
