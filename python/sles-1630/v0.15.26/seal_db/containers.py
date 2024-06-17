import seal_secrets_manager
from dependency_injector import containers, providers

from .authentication import DefaultAuthentication
from .authentication import Service as AuthenticationService
from .connector import Connector
from .paginator import Paginator
from .rds_password import Service as RDSPasswordService
from .settings import AuthenticationProvider, Settings


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()

    settings: providers.Singleton[Settings] = providers.Singleton(
        Settings.model_validate, config
    )

    secrets_manager: providers.Container[
        seal_secrets_manager.Container
    ] = providers.Container(
        seal_secrets_manager.Container,
        config=config.secrets_manager,
    )

    default_authentication_service: providers.Singleton[
        AuthenticationService
    ] = providers.Singleton(
        DefaultAuthentication,
        settings=settings.provided.connection,
    )
    rds_password_secret: providers.Singleton[
        seal_secrets_manager.Secret
    ] = providers.Singleton(
        seal_secrets_manager.Secret,
        service=secrets_manager.service,
        secret_id=settings.provided.connection.password,
    )
    rds_password_service: providers.Singleton[
        AuthenticationService
    ] = providers.Singleton(
        RDSPasswordService,
        rds_password_secret=rds_password_secret,
        settings=settings.provided.connection,
    )

    authentication_service: providers.Provider[
        AuthenticationService
    ] = providers.Selector(
        selector=settings.provided.connection.authentication_provider.value,
        **{
            AuthenticationProvider.default.value: default_authentication_service,
            AuthenticationProvider.rds_password.value: rds_password_service,
        }
    )

    connector = providers.Singleton(
        Connector,
        settings=settings.provided.connection,
        authentication_service=authentication_service,
    )

    paginator = providers.Singleton(
        Paginator,
        session_factory=connector.provided.session,
        settings=settings.provided.pagination,
        # (#860rhf1aa) for debugging the occasional authentication failure
        authentication_service=authentication_service,
    )
