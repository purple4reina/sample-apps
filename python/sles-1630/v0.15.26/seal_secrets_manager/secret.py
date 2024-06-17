import typing

from .service import Service


class Secret:
    def __init__(
        self,
        service: Service,
        secret_id: str,
    ) -> None:
        self._service = service
        self._secret_id = secret_id
        self._secret_value: typing.Optional[str] = None

    @property
    def value(self) -> str:
        if self._secret_value is None:
            self._secret_value = self._service.get_secret_value(self._secret_id)
        return self._secret_value
