import abc
import typing

from .settings import ConnectionSettings


class Service(abc.ABC):
    def __init__(self, settings: ConnectionSettings) -> None:
        self._settings = settings

    @abc.abstractmethod
    def get_password(
        self,
    ) -> typing.Optional[str]:
        return None

    @abc.abstractmethod
    def get_cert_path(self) -> typing.Optional[str]:
        return None


class DefaultAuthentication(Service):
    def get_password(
        self,
    ) -> typing.Optional[str]:
        return self._settings.password

    def get_cert_path(self) -> typing.Optional[str]:
        return None
