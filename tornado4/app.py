from newrelic.agent import function_trace

import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.write('*')
        self.finish()


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
