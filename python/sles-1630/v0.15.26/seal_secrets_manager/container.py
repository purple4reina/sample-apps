from dependency_injector import containers, providers

from .client import Client
from .service import Service
from .settings import Settings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings: providers.Singleton[Settings] = providers.Singleton(
        Settings.model_validate, config
    )

    client: providers.Singleton[Client] = providers.Singleton(
        Client,
        settings=settings,
    )

    service: providers.Callable[Service] = providers.Callable(
        Service,
        client=client,
        settings=settings,
    )
