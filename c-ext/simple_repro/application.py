import wrapt

def _log(*args):
    color_off = '\033[0m'
    blue = '\033[0;34m'
    print(blue + ' '.join(map(str, args)) + color_off)

@wrapt.function_wrapper
def wrapper(wrapped, instance, args, kwargs):
    _log('wrapper')
    return wrapped(*args, **kwargs)

class WSGIHandler(object):
    @wrapper
    def __call__(self, environ, start_response):
        _log('__call__')
        raise Exception('ooops!')

application = WSGIHandler()
