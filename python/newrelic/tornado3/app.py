import time

import tornado.gen
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient


class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        yield client.fetch('http://example.com')
        self.write('*')


def make_app():
    return tornado.web.Application(
        [
            (r'/', MainHandler),
        ],
        debug=True,
    )



if __name__ == '__main__':
    # sets up debugging to stdout
    tornado.options.parse_command_line()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
