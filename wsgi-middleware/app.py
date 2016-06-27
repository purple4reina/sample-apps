from middleware import HelloGoodbyer


def application(environ, start_response):
    status = '200 OK'
    response_headers = [('Content-type', 'text/plain')]

    # this returns a write() method, but we don't use it
    start_response(status, response_headers)

    # return a type that can be iterated across
    # this includes lists, strings, tuples, etc
    #
    # curl will print the contents of the response as they arrive while the
    # browser will wait till the connection is closed to render the response
    return ['Hello world\n']
    return LongIterable('hello world\n', 10)


class LongIterable(object):
    def __init__(self, return_val, total):
        self.return_val = return_val
        self.total = total
        self.count = 0

    def __iter__(self):
        return self

    def next(self):
        while self.count < self.total:
            self.count += 1
            return self.return_val
        raise StopIteration


wrapped_application = HelloGoodbyer(application)
