import sys

from newrelic.api.transaction import record_exception
from newrelic.common.object_wrapper import wrap_function_wrapper
from newrelic.core.config import ignore_status_code


def should_ignore(exc, value, tb):
    from falcon.http_error import HTTPError

    if isinstance(value, HTTPError):
        try:
            status_int = int(value.status.split()[0])
        except:
            return

        if ignore_status_code(status_int):
            return True


def _nr_wrap_API__handle_exception(wrapped, instance, args, kwargs):
    record_exception(*sys.exc_info(), ignore_errors=should_ignore)
    return wrapped(*args, **kwargs)


def instrument_falcon_api(module):
    wrap_function_wrapper(module, 'API._handle_exception',
            _nr_wrap_API__handle_exception)
