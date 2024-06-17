import typing

from aws_lambda_powertools.utilities.parser.models.apigw import (
    APIGatewayEventIdentity,
    APIGatewayProxyEventModel,
)
from fastapi import Request
from pydantic import BaseModel


class RequestContext(BaseModel):
    identity: typing.Optional[APIGatewayEventIdentity]
    request_id: typing.Optional[str]
    account_id: typing.Optional[str]


def mangum_request_to_context(
    request: Request,
) -> typing.Optional[RequestContext]:
    aws_raw_event = request.scope.get("aws.event")
    if aws_raw_event is None:
        return None
    aws_event = APIGatewayProxyEventModel.model_validate(aws_raw_event)
    return RequestContext(
        identity=aws_event.requestContext.identity,
        request_id=aws_event.requestContext.requestId,
        account_id=aws_event.requestContext.accountId,
    )
