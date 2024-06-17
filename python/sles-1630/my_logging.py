import base64
import functools
import json
import logging
import typing

import aws_lambda_powertools.logging.correlation_paths
from aws_lambda_powertools import Logger
from aws_lambda_powertools.logging import utils
from aws_lambda_powertools.logging.formatters.datadog import DatadogLogFormatter
from aws_lambda_powertools.shared.types import AnyCallableT

logger = Logger()
try:
    import boto3

    # Avoid "Found credentials in environment variables" info logs
    boto3.set_stream_logger(name="botocore.credentials", level=logging.WARNING)
except ImportError:  # nothing to do if we don't have boto3
    pass


def lambda_wrapper(
    handler: typing.Optional[typing.Callable[[AnyCallableT], AnyCallableT]] = None,
    log_event: bool = True,
    correlation_id_path: typing.Optional[
        str
    ] = aws_lambda_powertools.logging.correlation_paths.API_GATEWAY_REST,
) -> typing.Any:
    if handler is None:
        return functools.partial(
            lambda_wrapper,
            log_event=log_event,
            correlation_id_path=correlation_id_path,
        )

    wrapper = logger.inject_lambda_context(
        lambda_handler=handler,
        log_event=log_event,
        correlation_id_path=correlation_id_path,
    )

    @functools.wraps(handler)
    def decorate(
        event: typing.Any, context: typing.Any, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Any:
        try:
            event_authorizer = event["requestContext"]["authorizer"]
            add_user_info_to_logger(event_authorizer)
            if event["isBase64Encoded"] and event["body"]:
                decoded_message = base64.b64decode(event["body"]).decode("utf-8")
                logger.append_keys(decoded_body=json.loads(decoded_message))  # type: ignore[no-untyped-call]
        except:
            pass
        return wrapper(event, context, *args, **kwargs)  # type: ignore[call-arg]

    return decorate


def add_user_info_to_logger(
    event_authorizer: typing.Dict[typing.Any, typing.Any]
) -> None:
    user_info = get_user_session_from_event(
        event_authorizer=event_authorizer, attribute_name="user_session"
    )
    if user_info is not None:
        logger.append_keys(**user_info)  # type: ignore[no-untyped-call]
        return
    user_info = get_user_session_from_event(
        event_authorizer=event_authorizer, attribute_name="claims"
    )
    if user_info is not None:
        logger.append_keys(**user_info)  # type: ignore[no-untyped-call]
        return


def get_user_session_from_event(
    event_authorizer: typing.Any, attribute_name: str
) -> typing.Optional[typing.Dict[str, str]]:
    try:
        user_session = event_authorizer[attribute_name]
        if type(user_session) is str:
            user_session = json.loads(event_authorizer[attribute_name])
        tenant_id = user_session["tenantId"]
        user_sub = user_session["sub"]
        return {"tenant_id": tenant_id, "user_sub": user_sub}
    except:
        logger.debug("failed to extract user from session", exc_info=True)
        return None


def copy_config_to_registered_logger(
    log_level: typing.Optional[typing.Union[int, str]] = None,
    exclude: typing.Optional[typing.Set[str]] = None,
    include: typing.Optional[typing.Set[str]] = None,
) -> None:
    utils.copy_config_to_registered_loggers(
        source_logger=logger,
        log_level=log_level,
        exclude=exclude,
        include=include,
    )


# copy to all loggers installed by default
copy_config_to_registered_logger()
