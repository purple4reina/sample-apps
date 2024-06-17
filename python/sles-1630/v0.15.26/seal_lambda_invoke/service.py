import base64
import datetime
import ipaddress
import json
import typing

import botocore.response
import httpx
from aws_lambda_powertools.utilities.parser.models.apigw import (
    APIGatewayEventIdentity,
    APIGatewayEventRequestContext,
    APIGatewayProxyEventModel,
)
from seal_logging import logger

try:
    from ddtrace import tracer
except ImportError:
    logger.exception("Failed to import logging. Probably using local tests")
from pydantic import AwareDatetime, BaseModel, TypeAdapter

from . import context, exceptions, page
from .client import Client
from .settings import Settings

HttpMethod = typing.Literal["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]


class Service:
    def __init__(
        self,
        settings: Settings,
        client: Client,
    ) -> None:
        self._client = client
        self._settings = settings

    def invoke_lambda(
        self,
        function_name: str,
        payload: typing.Union[
            str, bytes, typing.IO[typing.Any], botocore.response.StreamingBody
        ],
    ) -> typing.Any:
        logger.debug("lib-lambda-invoke invoking lambda %s", function_name)
        result = self._client.lambda_client.invoke(
            FunctionName=function_name,
            InvocationType="RequestResponse",
            Payload=payload,
        )
        logger.debug("lib-lambda-invoke invoked lambda %s", function_name)
        # parse the output
        if not httpx.codes.is_success(result["StatusCode"]):
            function_error = result["FunctionError"]
            raise exceptions.SealLambdaInvokeException(function_error)

        payload = result["Payload"].read()
        return payload

    def invoke_http_proxy_lambda(
        self,
        function_name: str,
        path: str,
        method: HttpMethod,
        body: typing.Optional[bytes] = None,
        query: typing.Optional[typing.Dict[str, str]] = None,
        multi_value_query: typing.Optional[typing.Dict[str, typing.List[str]]] = None,
        headers: typing.Optional[typing.Dict[str, str]] = None,
        context: typing.Optional[context.RequestContext] = None,
    ) -> str:
        proxy_resource_path = "/{proxy+}"
        request_context = self._generate_request_context(
            http_method=method,
            request_path=path,
            proxy_resource_path=proxy_resource_path,
            user_context=context,
        )
        processed_multi_value_query: typing.Optional[
            typing.Dict[str, typing.List[str]]
        ] = None
        if query is not None:
            processed_multi_value_query = {key: [value] for key, value in query.items()}
        if multi_value_query is not None:
            if processed_multi_value_query is None:
                processed_multi_value_query = {}
            for key, value in multi_value_query.items():
                if key not in processed_multi_value_query:
                    processed_multi_value_query[key] = []
                processed_multi_value_query[key].extend(value)

        if headers is None:
            headers = {}

        request_payload = APIGatewayProxyEventModel(
            resource=proxy_resource_path,
            path=path,
            httpMethod=method,
            isBase64Encoded=True,
            queryStringParameters=query,
            multiValueQueryStringParameters=processed_multi_value_query,
            headers=headers,
            multiValueHeaders={},
            requestContext=request_context,
        )
        if body is not None:
            request_payload.body = base64.b64encode(body).decode("utf-8")

        payload = self.invoke_lambda(
            function_name=function_name,
            payload=request_payload.model_dump_json(),
        )

        parsed_payload = json.loads(payload)

        status_code: typing.Optional[int] = parsed_payload.get("statusCode")
        parsed_body: typing.Optional[str] = parsed_payload.get("body")
        if status_code is None:
            raise exceptions.SealLambdaInvokeHttpException(
                status_code=None,
                msg="No Status Code in response",
                content=json.dumps(parsed_payload),
            )
        if parsed_body is None:  # even if the body is empty, it should be a string
            raise exceptions.SealLambdaInvokeHttpException(
                status_code=status_code,
                msg="No body in response",
            )

        if parsed_payload["isBase64Encoded"]:
            parsed_body = base64.b64decode(parsed_body).decode("utf-8")

        if not httpx.codes.is_success(status_code):
            raise exceptions.SealLambdaInvokeHttpException(
                status_code=status_code,
                content=parsed_body,
            )

        return parsed_body

    def invoke_http_rest_lambda(
        self,
        function_name: str,
        path: str,
        method: HttpMethod,
        body: typing.Optional[typing.Dict[str, typing.Any]],
        query: typing.Optional[typing.Dict[str, str]] = None,
        multi_value_query: typing.Optional[typing.Dict[str, typing.List[str]]] = None,
        context: typing.Optional[context.RequestContext] = None,
    ) -> typing.Optional[typing.Dict[str, typing.Any]]:
        serialized_body = None
        if body is not None:
            serialized_body = json.dumps(body).encode("utf-8")
        raw_result = self.invoke_http_proxy_lambda(
            function_name=function_name,
            path=path,
            method=method,
            query=query,
            multi_value_query=multi_value_query,
            body=serialized_body,
            context=context,
        )

        # support endpoints that don't return a body, like for DELETE requests
        if not raw_result:
            return None

        result: typing.Dict[str, typing.Any] = json.loads(raw_result.encode("utf-8"))
        return result

    def invoke_paginated_list_http_lambda(
        self,
        item_type: typing.Type[page.T],
        function_name: str,
        path: str,
        query: typing.Optional[typing.Dict[str, str]] = None,
        multi_value_query: typing.Optional[typing.Dict[str, typing.List[str]]] = None,
        offset: int = 0,
        limit: int = 50,
        context: typing.Optional[context.RequestContext] = None,
    ) -> page.LimitOffsetPage[page.T]:
        processed_query: typing.Dict[str, str] = {
            "offset": str(offset),
            "limit": str(limit),
        }
        if query is not None:
            processed_query.update(query)

        parsed_body = self.invoke_http_proxy_lambda(
            function_name=function_name,
            path=path,
            method="GET",
            query=processed_query,
            multi_value_query=multi_value_query,
            body=None,
            context=context,
        )

        results_page = page.LimitOffsetPage[page.T].model_validate_json(parsed_body)
        if issubclass(item_type, BaseModel):
            results_page.items = [
                typing.cast(page.T, TypeAdapter(item_type).validate_python(item))
                for item in results_page.items
            ]

        return results_page

    def invoke_cursor_paginated_list_http_lambda(
        self,
        item_type: typing.Type[page.T],
        function_name: str,
        path: str,
        query: typing.Optional[typing.Dict[str, str]] = None,
        multi_value_query: typing.Optional[typing.Dict[str, typing.List[str]]] = None,
        cursor: typing.Optional[str] = None,
        size: int = 50,
        context: typing.Optional[context.RequestContext] = None,
    ) -> page.CursorPage[page.T]:
        processed_query: typing.Dict[str, str] = {
            "size": str(size),
        }
        if cursor is not None:
            processed_query["cursor"] = cursor
        if query is not None:
            processed_query.update(query)

        parsed_body = self.invoke_http_proxy_lambda(
            function_name=function_name,
            path=path,
            method="GET",
            query=processed_query,
            multi_value_query=multi_value_query,
            body=None,
            context=context,
        )

        results_page = page.CursorPage[page.T].model_validate_json(parsed_body)
        if issubclass(item_type, BaseModel):
            results_page.items = [
                typing.cast(page.T, TypeAdapter(item_type).validate_python(item))
                for item in results_page.items
            ]

        return results_page

    def _generate_request_context(
        self,
        http_method: HttpMethod,
        proxy_resource_path: str,
        request_path: str,
        account_id: str = "",
        api_id: str = "",
        stage: str = "",
        protocol: str = "",
        identity: APIGatewayEventIdentity = APIGatewayEventIdentity(
            sourceIp=ipaddress.IPv4Address("0.0.0.0")
        ),
        request_id: str = "",
        request_time: str = "",
        request_time_epoch: AwareDatetime = datetime.datetime(
            1970, 1, 1, tzinfo=datetime.timezone.utc
        ),
        user_context: typing.Optional[context.RequestContext] = None,
    ) -> APIGatewayEventRequestContext:
        if user_context is not None:
            if user_context.identity is not None:
                identity = user_context.identity
            if user_context.request_id is not None:
                request_id = user_context.request_id
            if user_context.account_id is not None:
                account_id = user_context.account_id

        return APIGatewayEventRequestContext(
            accountId=account_id,
            apiId=api_id,
            stage=stage,
            protocol=protocol,
            identity=identity,
            requestId=request_id,
            requestTime=request_time,
            requestTimeEpoch=request_time_epoch,
            httpMethod=http_method,
            resourcePath=proxy_resource_path,
            path=request_path,
        )

    def invoke_http_post_multipart(
        self,
        function_name: str,
        path: str,
        parts: typing.List[
            typing.Tuple[typing.Dict[str, str], bytes]
        ],  # headers, body for each part
        query: typing.Optional[typing.Dict[str, str]] = None,
        multi_value_query: typing.Optional[typing.Dict[str, typing.List[str]]] = None,
        context: typing.Optional[context.RequestContext] = None,
    ) -> typing.Optional[str]:
        # https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html
        boundary = "seal-lambda-invoke-boundary"
        serialized_body = b""
        for headers, body in parts:
            serialized_body += b"--" + boundary.encode("utf-8")
            for header_name, header_value in headers.items():
                serialized_body += b"\r\n" + header_name.encode("utf-8")
                serialized_body += b": " + header_value.encode("utf-8")
            serialized_body += b"\r\n\r\n" + body + b"\r\n"
        serialized_body += b"--" + boundary.encode("utf-8") + b"--\r\n"
        headers = {
            "Content-Type": f"multipart/form-data; boundary={boundary}",
        }

        return self.invoke_http_proxy_lambda(
            function_name=function_name,
            path=path,
            method="POST",
            query=query,
            multi_value_query=multi_value_query,
            body=serialized_body,
            headers=headers,
            context=context,
        )
