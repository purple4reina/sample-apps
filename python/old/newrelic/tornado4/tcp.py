import time

from tornado.gen import coroutine
from tornado.ioloop import IOLoop
from tornado.iostream import StreamClosedError
from tornado.tcpserver import TCPServer

import newrelic.agent


class MyTCPServer(TCPServer):

    @newrelic.agent.background_task()
    @coroutine
    def handle_stream(self, stream, address):
        while True:
            try:
                data = yield stream.read_until(b"\n")
                time.sleep(1)
                print('received data: %s' % data)
                yield stream.write(data)
            except StreamClosedError:
                break


if __name__ == '__main__':
    server = MyTCPServer()
    server.listen(8888)

    try:
        print('starting server')
        IOLoop.current().start()
    except KeyboardInterrupt:
        print('stopping server')
