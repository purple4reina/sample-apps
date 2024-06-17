import os
import typing

import alembic.command
import alembic.config

from .containers import Container
from .settings import Settings


def handler(
    _: typing.Dict[typing.Any, typing.Any], __: typing.Dict[str, typing.Any]
) -> typing.Dict[typing.Any, typing.Any]:
    # initialize the container
    container = Container()
    # load the settings
    settings = Settings()
    container.config.from_dict(settings.model_dump())
    # load the alembic config
    alembic_config = alembic.config.Config(
        os.path.join(os.path.dirname(__file__), "alembic", "alembic.ini")
    )
    alembic_config.attributes["container"] = container
    alembic.command.upgrade(alembic_config, "head")
    return {}
