from transform import hello_to_goodbye


class HelloGoodbyeIter:
    """
    Transform iterated output using hello_to_goodbye
    """

    def __init__(self, result):
        if hasattr(result, 'close'):
            self.close = result.close
        self._next = iter(result).next

    def __iter__(self):
        return self

    def next(self):
        # This is where the change is happening
        return hello_to_goodbye(self._next())


class HelloGoodbyer:

    def __init__(self, application):
        self.application = application

    # returns an iteratable
    def __call__(self, environ, start_response):

        # returns a function `write` which takes one argument, a string
        # (body_data) that is the contents of the page
        def start_hello_goodbye(status, response_headers):
            write = start_response(status, response_headers)

            # transform the text in body_data before sending it to `write`
            def write_hello_goodbye(body_data):
                # Why is it that the body is changed both here and in the Iter?
                return write(hello_to_goodbye(body_data))
            return write_hello_goodbye

        return HelloGoodbyeIter(self.application(environ, start_hello_goodbye))
