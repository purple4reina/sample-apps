import asyncio
import os
import re
import typing
from logging.config import fileConfig

from alembic import context
from alembic.autogenerate.api import AutogenContext
from sqlalchemy import MetaData, Unicode, engine_from_config, pool
from sqlalchemy.engine.base import Connection

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata: typing.Optional[MetaData] = None
if not typing.TYPE_CHECKING:
    import src.db.models

    target_metadata = src.db.models.Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.
config.set_main_option(
    "sqlalchemy.url",
    re.sub(
        r"\+[a-zA-Z0-9]*:",
        ":",
        os.environ.get(
            "db__connection__url",
            "postgresql://postgres:password@localhost:5432",
        ),
    ),  # ignore the async driver
)


from importlib.machinery import SourceFileLoader

SourceFileLoader(
    "", os.path.join(os.path.dirname(__file__), "..", "compatibility.py")
).load_module()


# default template
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    asyncio.get_event_loop().run_until_complete(async_run_migrations_online())


async def async_run_migrations_online() -> None:
    container = "container"
    if container in context.config.attributes:
        # connected to the real DB
        # create a session
        async with context.config.attributes[
            "container"
        ].connector()._engine.connect() as connection:
            await connection.run_sync(sync_run_migrations_online)
    else:
        # connected to the test DB
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, default={}),
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
        )
        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata,
            )

            with context.begin_transaction():
                context.run_migrations()


def sync_run_migrations_online(connection: Connection) -> None:
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
    )

    with context.begin_transaction():
        context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
