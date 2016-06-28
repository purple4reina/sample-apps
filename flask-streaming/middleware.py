class HelloGoodbyeIter:

    def __init__(self, result):
        if hasattr(result, 'close'):
            self.close = result.close
        self._next = iter(result).next

    def __iter__(self):
        return self

    def next(self):
        return hello_to_goodbye(self._next())

class HelloGoodbyer:

    def __init__(self, application):
        self.application = application

    def __call__(self, environ, start_response):
        def start_hello_goodbye(status, response_headers):
            write = start_response(status, response_headers)
            def write_hello_goodbye(body_data):
                return write(hello_to_goodbye(body_data))
            return write_hello_goodbye
        return HelloGoodbyeIter(self.application(environ, start_hello_goodbye))

def hello_to_goodbye(data):
    return data.replace('hello', 'goodbye').replace('Hello',
            'Goodbye').replace('HELLO', 'GOODBYE')
