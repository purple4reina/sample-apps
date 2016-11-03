import bottle

from functools import wraps

#from lib.consts import OPTIONS, POST, PUT, DELETE
OPTIONS = 'OPTIONS'
POST = 'POST'
PUT = 'PUT'
DELETE = 'DELETE'


def _options_router(route, method, app=None):
    if app is None:
        app = bottle.app()

    def wrapper(f):
        @app.route(route, method=method)
        @app.route(route, method=OPTIONS)
        def wrap(*args, **kwargs):
            if bottle.request.method == OPTIONS:
                return ""
            return f(*args, **kwargs)
        return wrap
    return wrapper


def post(route, app=None):
    return _options_router(route, method=POST, app=app)


def put(route, app=None):
    return _options_router(route, method=PUT, app=app)


def delete(route, app=None):
    return _options_router(route, method=DELETE, app=app)


def get(route, app=None):
    if app is None:
        app = bottle.app()

    def wrapper(f):
        @app.get(route)
        @wraps(f)
        def wrap(*args, **kwargs):
            return f(*args, **kwargs)
        return wrap
    return wrapper


__all__ = [
    "delete",
    "get",
    "post",
    "put",
]
