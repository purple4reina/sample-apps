import seal_lambda_invoke
from dependency_injector import containers, providers

from .client import Client
from .service import Service
from .settings import Settings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings: providers.Singleton[Settings] = providers.Singleton(
        Settings.model_validate, config
    )

    lambda_invoke: providers.Container[
        seal_lambda_invoke.Container
    ] = providers.Container(
        seal_lambda_invoke.Container,
        config=config.lambda_invoke,
    )

    client: providers.Singleton[Client] = providers.Singleton(
        Client,
        settings=settings,
        lambda_service=lambda_invoke.service,
    )

    service: providers.Callable[Service] = providers.Callable(
        Service,
        client=client,
        settings=settings,
    )
