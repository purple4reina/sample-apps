import seal_secrets_manager
from dependency_injector import containers, providers

from . import models
from .client import Client
from .cloudfront import Signer as CloudfrontSigner
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


class CloudfrontSignerContainer(containers.DeclarativeContainer):
    secrets_manager_service: providers.Dependency[
        seal_secrets_manager.Service
    ] = providers.Dependency(
        instance_of=seal_secrets_manager.Service,
    )

    settings: providers.Dependency[models.BucketCloudfrontInfo] = providers.Dependency(
        instance_of=models.BucketCloudfrontInfo,
    )

    signing_private_key: providers.Singleton[
        seal_secrets_manager.Secret
    ] = providers.Singleton(
        seal_secrets_manager.Secret,
        service=secrets_manager_service,
        secret_id=settings.provided.signing_key_secret_id,
    )

    signer: providers.Singleton[CloudfrontSigner] = providers.Singleton(
        CloudfrontSigner,
        domain_name=settings.provided.domain_name,
        signing_key_id=settings.provided.signing_key_id,
        signing_private_key=signing_private_key.provided.value,
    )
