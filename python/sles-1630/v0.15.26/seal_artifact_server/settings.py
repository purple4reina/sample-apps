import seal_lambda_invoke
from pydantic import BaseModel


class Settings(BaseModel):
    artifact_management_lambda_name: str
    lambda_invoke: seal_lambda_invoke.Settings
