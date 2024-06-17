import seal_lambda_invoke

from . import settings


class Client:
    def __init__(
        self,
        settings: settings.Settings,
        lambda_service: seal_lambda_invoke.Service,
    ) -> None:
        self._settings = settings
        self.lambda_service = lambda_service
