import tornado.gen
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.httpclient


class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self):
        self.finish('*')


class FetchHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        resp = yield client.fetch('http://localhost:8888')
        self.write('*')
        print 'resp.code: ', resp.code


def make_app():
    return tornado.web.Application(
        [
            (r'/', MainHandler),
            (r'/fetch', FetchHandler),
        ],
        debug=True,
    )



if __name__ == '__main__':
    # sets up debugging to stdout
    tornado.options.parse_command_line()

    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()
