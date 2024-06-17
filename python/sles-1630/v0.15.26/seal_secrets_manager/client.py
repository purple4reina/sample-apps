import boto3
import botocore.config
import mypy_boto3_secretsmanager.client

from .settings import Settings


class Client:
    def __init__(self, settings: Settings) -> None:
        config = botocore.config.Config(
            connect_timeout=settings.aws_connect_timeout_in_seconds,
            read_timeout=settings.aws_read_timeout_in_seconds,
            retries={"max_attempts": settings.aws_max_attempts},
        )
        self.secrets_manager_client: mypy_boto3_secretsmanager.client.SecretsManagerClient = boto3.client(
            service_name="secretsmanager",
            config=config,
        )
