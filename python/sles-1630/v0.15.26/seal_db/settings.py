import enum
import typing

import seal_secrets_manager
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy import pool as sqlalchemy_pool
from typing_extensions import Annotated


class AuthenticationProvider(enum.Enum):
    default = "default"
    rds_password = "rds_password"


class ConnectionSettings(BaseModel):
    authentication_provider: AuthenticationProvider = AuthenticationProvider.default
    driver: str
    username: typing.Optional[str] = None
    password: typing.Optional[str] = None
    host: typing.Optional[str] = None
    port: typing.Optional[int] = None
    database: typing.Optional[str] = None
    echo: bool = False
    timeout_in_seconds: Annotated[int, Field(ge=1)] = 5  # in seconds
    sslmode: typing.Optional[str] = None
    pool_class: typing.Optional[typing.Type[sqlalchemy_pool.Pool]] = None
    # in seconds, RDP idle_client_timeout value is set to 3600 seconds, so recycling after 3000 should be safe
    pool_recycle: typing.Optional[int] = 3000
    # aws
    aws_connect_timeout_in_seconds: int = 1
    aws_read_timeout_in_seconds: int = 30
    aws_max_attempts: int = 0


class PaginationSettings(BaseModel):
    max_page_size: Annotated[int, Field(ge=1)] = 100
    limit: Annotated[int, Field(ge=1, le=max_page_size)] = 25


class Settings(BaseSettings):
    secrets_manager: seal_secrets_manager.Settings
    connection: ConnectionSettings
    pagination: PaginationSettings

    model_config = SettingsConfigDict(env_nested_delimiter="__")
