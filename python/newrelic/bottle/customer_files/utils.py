import functools
import inspect
from os import environ
import re
import sys
import time
import traceback

import ujson

import bottle
import cherrypy
from cherrypy import _cperror
from contextlib import contextmanager
import logging
import logging.handlers
from logging.handlers import SysLogHandler
from logging import StreamHandler
from peak.util.proxies import ObjectProxy
import raven
import raven.contrib.bottle

from lib.bottle.plugins.activity_id import activity_id_plugin
from lib.errors import BaseError
from lib.server.consts import JSON_MIMETYPE
from lib.utils.datadog import send_metric

LOG_FUNC_PAT = re.compile('^([.\w]+)\(')

TEST_MODE = False

logger = None
app_logger_formatter = None
LOG_CONFIG_PATH = environ.get('API_LOG_CONFIG_PATH', '/etc/peloton/api/logconfig.json')
DEFAULT_LOG_LEVEL = 'info'

LOG_LEVEL_MAP = {'info': logging.INFO,
                 'warning': logging.WARNING,
                 'error': logging.ERROR,
                 'critical': logging.CRITICAL,
                 'debug': logging.DEBUG}


def catch(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except BaseError as e:
            throw(e)

    return wrapper


def throw(e):
    raise bottle.HTTPError(
        e.response_code,
        body=repr(e),
        exception=e if isinstance(e, BaseError) else e())


def common_bottle_error_handler(bottle_httperror):
    if bottle_httperror.status_code == 401:
        bottle.response.headers["WWW-Authenticate"] = \
            'FormBased realm="Peloton"'

    if logger:
        logger.error("%s %s %s" % (bottle.request.method,
                                   bottle_httperror.status_code,
                                   bottle.request.url))

    return jsonify_bottle_error(bottle_httperror)


def jsonify_bottle_error(bottle_httperror):
    bottle.response.content_type = JSON_MIMETYPE
    exception = bottle_httperror.exception
    response_code = bottle_httperror.status_code
    message = str(exception) if exception else bottle_httperror.status

    return _format_common_error_body(exception,
                                     status_code=response_code,
                                     message=message)


def common_cherrypy_error_handler():
    e_type, e, _ = _cperror._exc_info()
    if isinstance(e, BaseError):
        status = e.response_code
    else:
        status = 500

    cherrypy.response.status = status
    cherrypy.response.headers["Content-Type"] = JSON_MIMETYPE
    cherrypy.response.body = _format_common_error_body(e, status_code=status)


def _format_common_error_body(e, status_code=None, message=None):
    return ujson.dumps({
        "status": status_code or e.response_code,
        "error_code": getattr(e, "code", None),
        "subcode": getattr(e, "subcode", None),
        "message": message or str(e),
        "details": getattr(e, "details", None),
    })


# -- #

def bottle_body_as_json(*args):
    body = bottle.request.body.read()
    body = ujson.loads(body) if body else {}

    if not args:
        return body
    if len(args) == 1:
        return body.get(args[0])
    return (body.get(i) for i in args)


class Extras(object):

    def __init__(self, extras=None):
        # Shallow copy
        self._extras = dict(extras if extras is not None else {})

    def __setattr__(self, key, value):
        if key.startswith('_'):
            return object.__setattr__(self, key, value)

        self._extras[key] = value

    def __call__(self):
        t = time.time()
        try:
            try:
                yield self
            except Exception as e:
                self._extras['_exception'] = repr(e)
                raise
        finally:
            self._time = time.time() - t

    def __enter__(self):
        self.time = self._time = time.time()
        return self

    def __exit__(self, error_type, error_value, error_traceback):
        self.duration = time.time() - self._time

        stack = [(x[0], x[1]) for x in traceback.extract_stack(limit=10)]

        while 'lib/server/utils.py' in stack[-1][0]:
            stack.pop()

        while 'contextlib.py' in stack[-1][0]:
            stack.pop()

        self.file = "%s:%s" % stack[-1]

        if error_type and error_value and error_traceback:
            self.error = error_value

    def __repr__(self):
        return repr(self._extras)

    def as_dict(self):
        return self._extras


def ContextLogger(happy=None, sad=None, use_object_ids=False):
    """A context_logger class factory.

    happy is a method to call on non-exceptional behavior, sad
    is a method to call if an exception is raised either in the body of
    the context manager, or by the method being decorated.

    If use_object_ids is True, any arg in the list of varargs which has an
    id attribute will be represented as the object's name and its id attribute.
    If the context logger is used as a decorator and the log message is being
    inferred, then any parameter with an id attribute will be represented as
    the object's name and its id attribute.

    Returns a context_logger class constructed as specified.
    """
    class context_logger(_ContextLogger):
        _happy = happy
        _sad = sad
        _use_object_ids = use_object_ids

    return context_logger


class _ContextLogger(object):

    """A context logger that can be used as a decorator and a context manager.

    Prefer to not use this class directly. Instead, build a custom context
    logger using the ContextLogger class factory.

    The class can be used as both a decorator and a context manager, and either
    usage accepts the parameters allowed by the class's init method.

    Decorator usage:
        from lib.server.utils import ContextLogger

        context_logger = ContextLogger(happy=somefunc, sad=otherfunc, ...)

        @context_logger()
        def my_func(param_a, param_b=None, param_c=3, *args):
            # do stuff
            ...

    In the decorator usage, if no log template is specified any vararg
    parameters passed to the decorator function will be ignored and a
    log message will be constructed based upon the signature of the
    decorated function and the parameters for the specific call. The message
    will be composed using the following rules:
      * The constructed log message will resemble the method signature e.g.
        method_name(param1=value1, param2=value2)
      * All parameters will be shown with the parameter name, regardless of
        whether they were specified as keyword or positional parameters.
      * Positional parameters will appear first, followed by defaulted parameters.
        These parameters will be in the order specified in the function signature.
        Next will be vararg parameters in the order they occur in the call, and
        finally keyword parameters. Keyword parameters will be in sorted order
        regardless of the order they appear in the call.
      * If the class variable _use_object_ids is True, then any parameter value
        that is an object with an 'id' attribute will be represented as
        '{object_class_name}(id->{id})'.

    Context manager usage:

        from lib.server.utils import context_logger

        with context_logger(happyfunc, sadfunc, '%s is happening', 'logging', ...) as logger:
            # do stuff
            ...

    Note that when using the context_logger as a context manager, there is
    likely no advantage gained by constructing a custom context_logger class
    using ContextLogger(...) since most such usages will likely require the use
    of vararg parameters, making it necessary to specify all the positional
    parameters on each usage.
    """
    _happy = None
    _sad = None
    _use_object_ids = False

    def __init__(self, happy=None, sad=None, log=None, *args, **extras):
        """Initialize the context logger.

        When used as a context manager, logging occurs when the context
        manager is exited. When used as a decorator, logging occurs after
        returning from the callee.

        happy is a method to call on non-exceptional behavior, sad
        is a method to call if an exception is raised either in the body of
        the context manager, or by the method being decorated. Both methods
        should have signatures identical to those of the log methods of the
        python logging module. Both happy and sad may also be set to None,
        in which case no logging will occur.

        log, args, and kwargs will be passed to the handler methods: happy and
        sad.
        """
        if happy:
            self._happy = happy
        if sad:
            self._sad = sad
        self.log = log
        self.args = args if not self._use_object_ids else self._args_using_object_ids(args)
        self.extras = Extras(extras)

    @staticmethod
    def _args_using_object_ids(args):
        return tuple(
            '{name}(id->{id})'.format(
                name=getattr(type(arg), '__name__'),
                id=getattr(arg, 'id'))
            if hasattr(arg, 'id') else arg for arg in args)

    @contextmanager
    def _call_context(self, f, args, kwargs):
        log_orig = self.log
        args_orig = self.args
        try:
            if not self.log:
                self.log = self._format_log_message(f, args, kwargs)
                self.args = ()
            yield
        finally:
            self.log = log_orig
            self.args = args_orig

    def __call__(self, f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            with self._call_context(f, args, kwargs):
                with self:
                    return f(*args, **kwargs)
        return wrapper

    def __enter__(self):
        self.start = time.time()
        self.log_func = self._happy
        self.kwargs = {}
        self.extras.__enter__()
        return self.extras

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.extras.__exit__(exc_type, exc_val, exc_tb)

        stop = time.time()
        self.extras._start = self.start
        self.extras._stop = stop
        self.extras._duration = stop - self.start

        if hasattr(bottle.request, 'activity_id'):
            self.extras.activity_id = bottle.request.activity_id

        if exc_type:
            self.log_func = self._sad
            self.kwargs['exc_info'] = True
        if self.log_func:
            # Extra is for loggly, data is for sentry
            self.kwargs['extra'] = {
                'extra': ujson.dumps(self.extras.as_dict()),
                'data': self.extras.as_dict(),
            }
            if not TEST_MODE:
                self.log_func(self.log, *self.args, **self.kwargs)
                mat = LOG_FUNC_PAT.match(self.log)
                if not mat:
                    return
                func_name = mat.group(1)
                send_metric('python_timing', self.extras._duration,
                            tags=['function:%s' % func_name])

    def _format_log_message(self, f, args, kwargs):
        argspec = inspect.getargspec(f)
        kwargs = kwargs.copy()

        try:
            defaults = {}
            if argspec.defaults:
                defaults.update(zip(argspec.args[-len(argspec.defaults):], argspec.defaults))
            positional = zip(argspec.args, args)
            defaulted = dict((k, defaults[k]) for k in argspec.args[len(positional):]
                             if k not in kwargs)
            positional.extend((arg, defaulted.get(arg) if arg in defaulted else kwargs.pop(arg))
                              for arg in argspec.args[len(positional):])
            varargs = [(None, v) for v in args[len(positional):]]
            keyword = sorted(kwargs.items())
            params = positional + varargs + keyword
        except Exception:
            return ('{name}(Error: log message could not be inferred from call '
                    'signature. args: {args}, kwargs: {kwargs})').format(
                name=self._func_repr(f),
                args=args,
                kwargs=kwargs)

        return '{name}({params})'.format(
            name=self._func_repr(f),
            params=', '.join(self._param_repr(param) for param in params))

    @staticmethod
    def _func_repr(func):
        return func.__name__

    def _param_repr(self, item):
        param, value = item

        if self._use_object_ids and hasattr(value, 'id'):
            value = '{name}(id->{id})'.format(
                name=getattr(type(value), '__name__'),
                id=getattr(value, 'id'))
        else:
            value = repr(value)

        return '{param}={value}'.format(param=param, value=value) if param else value


context_logger = ContextLogger()


class Zilch(object):

    """A variation of None that is worse than None."""

    def __repr__(self):
        return ''

    def __str__(self):
        return ''


class ForgivingDict(dict):

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            return Zilch()


class ForgivingFormattingString(str):

    def __mod__(self, obj):
        if isinstance(obj, dict):
            obj = ForgivingDict(obj)
        return str.__mod__(self, obj)

stderr = ObjectProxy(sys.stderr)


def get_app_logger(log_name):
    app_logger = logging.getLogger('peloton-api.' + log_name)
    global app_logger_formatter, LOG_CONFIG_PATH
    if not app_logger_formatter:
        root_logger = logging.getLogger('peloton-api')
        if (environ.get('USER', 'peloton') != 'peloton' or any(
                True for frame in traceback.extract_stack() if 'nose/loader.py' in frame[0])):
            syslog_handler = StreamHandler(stream=stderr)
        else:
            syslog_handler = SysLogHandler(address='/dev/log',
                                           facility=SysLogHandler.LOG_LOCAL3)
        format_string = '%(name)s %(levelname)s %(message)s %(extra)s'
        format_string = ForgivingFormattingString(format_string)
        app_logger_formatter = logging.Formatter(format_string)
        syslog_handler.setFormatter(app_logger_formatter)
        root_logger.addHandler(syslog_handler)
        try:
            log_file = open(environ.get('LOG_CONFIG_PATH', LOG_CONFIG_PATH))
        except IOError:
            log_file = open('/dev/null')
        logging_config = ujson.loads(log_file.read() or '{}')
        log_level = logging_config.get('LEVEL', DEFAULT_LOG_LEVEL)
        root_logger.setLevel(LOG_LEVEL_MAP[log_level.lower()])

    return app_logger


def make_sentry_client(conf):
    client = raven.Client(dsn=conf.sentry_url,
                          processors=('lib.utils.raven.ReformatJSONData',
                                      'raven.processors.SanitizePasswordsProcessor',))
    return client


def initialize_bottle_root_app(app, conf, log_name='peloton'):
    if not conf.is_prod:
        bottle.debug(True)

    register_error_handlers(app)

    return app


def initialize_bottle_sentry_app(app, client, is_local=False):
    app.install(activity_id_plugin)

    if not is_local:
        app.catchall = False
        app = raven.contrib.bottle.Sentry(app, client)

    return app


def register_error_handlers(app):

    @app.error(400)
    @app.error(401)
    @app.error(403)
    @app.error(404)
    @app.error(500)
    def error_handler(e):
        return common_bottle_error_handler(e)
