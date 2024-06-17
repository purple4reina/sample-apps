from .client import Client
from .settings import Settings


class Service:
    def __init__(
        self,
        settings: Settings,
        client: Client,
    ) -> None:
        self._client = client
        self._settings = settings

    def get_secret_value(self, secret_id: str) -> str:
        secret_data = self._client.secrets_manager_client.get_secret_value(
            SecretId=secret_id
        )

        return secret_data["SecretString"]
