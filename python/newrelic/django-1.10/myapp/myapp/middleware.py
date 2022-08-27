import time

def happy_go_lucky(get_response):
    def happy_middleware(request):
        print 'I\'m happy today'
        response = get_response(request)
        print 'I\'m still happy today'
        return response
    return happy_middleware

def angry_dog(get_response):
    def angry_middleware(request):
        print 'I\'m really mad today'
        response = get_response(request)
        print 'I\'m still really mad today'
        return response
    return angry_middleware

class SimpleMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print 'This is going to be simple'
        response = self.get_response(request)
        print 'It was totally simple'
        return response

class SimpleMiddlewareClass(object):
    def process_request(self, request):
        time.sleep(1)
