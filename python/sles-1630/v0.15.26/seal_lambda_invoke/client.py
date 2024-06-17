import boto3
import botocore.config
import mypy_boto3_lambda.client
from seal_logging import logger

from . import settings


class Client:
    def __init__(self, settings: settings.Settings) -> None:
        logger.debug("lib-lambda-invoke creating clients")
        config = botocore.config.Config(
            connect_timeout=settings.aws_connect_timeout_in_seconds,
            read_timeout=settings.aws_read_timeout_in_seconds,
            retries={"max_attempts": settings.aws_max_attempts},
        )
        self.lambda_client: mypy_boto3_lambda.client.LambdaClient = boto3.client(
            service_name="lambda",
            config=config,
        )
        logger.debug("lib-lambda-invoke clients created")
