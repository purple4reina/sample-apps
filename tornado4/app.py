import time
from testingtools import printcolor as pcolor

import tornado.gen
import tornado.httpclient
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write('*')


class SlowHandler(tornado.web.RequestHandler):
    def get(self):
        pcolor.print_blue('/slow/...')
        cnt = 5
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


class CoroutineHandler(tornado.web.RequestHandler):

    @tornado.gen.coroutine
    def get(self):
        tornado.httpclient.AsyncHTTPClient.configure(
                'tornado.simple_httpclient.SimpleAsyncHTTPClient')
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield client.fetch('http://localhost:5000')
        self.write(resp.body)

class CurlCoroutineHandler(CoroutineHandler):

    @tornado.gen.coroutine
    def get(self):
        tornado.httpclient.AsyncHTTPClient.configure(
                'tornado.curl_httpclient.CurlAsyncHTTPClient')
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield client.fetch('http://localhost:5000')
        self.write(resp.body)

def make_app():
    return tornado.web.Application(
        [
            (r'/', MainHandler),
            (r'/slow/?', SlowHandler),
            (r'/error/?', ErrorHandler),
            (r'/socket/?', WebSocketHandler),
            (r'/async/?', AsyncHandler),
            (r'/coroutine/?', CoroutineHandler),
            (r'/coroutine/curl/?', CurlCoroutineHandler),
        ],
        debug=True,
    )


if __name__ == '__main__':
    # sets up debugging to stdout
    tornado.options.parse_command_line()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
