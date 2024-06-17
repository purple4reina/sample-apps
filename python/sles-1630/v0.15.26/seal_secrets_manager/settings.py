from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    aws_connect_timeout_in_seconds: int = 1
    aws_read_timeout_in_seconds: int = 1
    aws_max_attempts: int = 0
    model_config = SettingsConfigDict(env_nested_delimiter="__")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
