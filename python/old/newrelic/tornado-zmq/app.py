import os
import time

import tornado.httpclient
import tornado.options
import tornado.web
import tornado.ioloop
import zmq.eventloop

URL = 'http://localhost:8888/'
USE_CURL_HTTPCLIENT = os.environ.get('USE_CURL_HTTPCLIENT', False)

class MainHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, body):
        self.body = body
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch(
            URL + self.body,
            header_callback=self.header_callback,
            streaming_callback=self.streaming_callback,
            prepare_curl_callback=self.prepare_curl_callback,
            body=self.body,
            method='POST',
        )
        self.finish()

    def post(self, body):
        self.write(self.request.body)

    def callback(self, response):
        print('Response body: ', response.body)
        if response.code != 200:
            response.rethrow()

    def header_callback(self, header):
        header = header.strip()
        if header:
            print('header: ', header)
            eventloop.add_callback(self.function)

    def streaming_callback(self, chunk):
        print('chunk length: ', len(chunk))

    def prepare_curl_callback(self, curl):
        pass

    def function(self):
        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch(
            URL + self.body,
            callback=self.callback,
            body=self.body,
            method='POST',
        )

class AsyncHandler(tornado.web.RequestHandler):

    @tornado.web.asynchronous
    def get(self):
        print('USE_CURL_HTTPCLIENT: ', USE_CURL_HTTPCLIENT)
        self.finished = False

        client = tornado.httpclient.AsyncHTTPClient()
        client.fetch(
            URL + 'o',
            callback=self.callback,
            streaming_callback=self.callback,
            body='0',
            method='POST',
        )

        eventloop.add_callback(self.callback)

    def callback(self, *args, **kwargs):
        if not self.finished:
            eventloop.add_callback(lambda : self.finish('*'))
            self.finished = True

if __name__ == '__main__':
    # use zeromq for the event loop
    eventloop = zmq.eventloop.ioloop.ZMQIOLoop.current()

    tornado.options.parse_command_line()  # sets up debugging to stdout

    if USE_CURL_HTTPCLIENT:
        # use curl_httpclient for all httpclients
        tornado.httpclient.AsyncHTTPClient.configure(
            'tornado.curl_httpclient.CurlAsyncHTTPClient')

    app = tornado.web.Application([
        (r'/(\w+)/?', MainHandler),
        (r'/', AsyncHandler),
    ], debug=True)
    app.listen(os.environ.get('USE_PORT', 8888))

    eventloop.start()
