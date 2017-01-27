import tornado.gen
import tornado.options
import tornado.web
import tornado.httpclient
import zmq.eventloop

def callback(resp):
    print 'Response code: %s' % resp.code

class MainHandler(tornado.web.RequestHandler):
    @tornado.gen.coroutine
    def get(self):
        client = tornado.httpclient.AsyncHTTPClient()
        self.write('*')

        # this works fine
        client.fetch('http://example.com')

        # but this throws a traceback
        client.fetch('http://example.com', callback=callback)

if __name__ == '__main__':
    # use zeromq for the event loop
    eventloop = zmq.eventloop.ioloop.ZMQIOLoop.current()

    tornado.options.parse_command_line()  # sets up debugging to stdout

    # use curl_httpclient for all httpclients
    tornado.httpclient.AsyncHTTPClient.configure(
            'tornado.curl_httpclient.CurlAsyncHTTPClient')

    app = tornado.web.Application([(r'/', MainHandler)], debug=True)
    app.listen(8888)

    eventloop.start()
