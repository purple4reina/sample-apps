from pydantic import BaseModel


class Settings(BaseModel):
    aws_connect_timeout_in_seconds: int = 1
    aws_read_timeout_in_seconds: int = 30
    aws_max_attempts: int = 3
