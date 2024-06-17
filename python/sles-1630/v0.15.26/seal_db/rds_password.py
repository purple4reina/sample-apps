import typing

import seal_secrets_manager
from pydantic import BaseModel

from .authentication import Service as AuthenticationService
from .certs import rds_cert_path
from .settings import ConnectionSettings


class RDSSecretManagerCredentials(BaseModel):
    engine: typing.Literal["postgres"]
    host: str
    username: str
    password: str
    dbname: str
    port: int


class Service(AuthenticationService):
    def __init__(
        self,
        settings: ConnectionSettings,
        rds_password_secret: seal_secrets_manager.Secret,
    ) -> None:
        super().__init__(settings=settings)
        self._rds_password_secret = rds_password_secret

    def get_password(
        self,
    ) -> str:
        raw_credentials = self._rds_password_secret.value
        credentials = RDSSecretManagerCredentials.model_validate_json(raw_credentials)

        return credentials.password

    def get_cert_path(self) -> typing.Optional[str]:
        return rds_cert_path
