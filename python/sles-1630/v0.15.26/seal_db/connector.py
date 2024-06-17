import ssl
import typing
from asyncio import current_task
from contextlib import asynccontextmanager

import sqlalchemy
import sqlalchemy.ext.asyncio
import sqlalchemy.orm
from seal_logging import logger
from sqlalchemy.sql import text

from .authentication import Service as AuthenticationService
from .settings import ConnectionSettings


class Connector:
    def __init__(
        self,
        settings: ConnectionSettings,
        authentication_service: AuthenticationService,
    ) -> None:
        logger.debug("Creating database connector")
        url = sqlalchemy.engine.URL.create(
            drivername=settings.driver,
            username=settings.username,
            password=authentication_service.get_password(),
            host=settings.host,
            port=settings.port,
            database=settings.database,
        )
        connect_args: typing.Dict[str, typing.Any] = {
            "timeout": settings.timeout_in_seconds,
        }
        if settings.sslmode is not None:
            ssl_context = ssl.create_default_context(
                purpose=ssl.Purpose.CLIENT_AUTH,
                capath=authentication_service.get_cert_path(),
            )
            connect_args["ssl"] = ssl_context

        self._engine = sqlalchemy.ext.asyncio.create_async_engine(
            url=url,
            echo=settings.echo,
            connect_args=connect_args,
            poolclass=settings.pool_class,
            pool_recycle=settings.pool_recycle,
        )
        self._session_factory = sqlalchemy.ext.asyncio.async_sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=self._engine,
        )

    @asynccontextmanager
    async def session(
        self,
    ) -> typing.AsyncIterator[sqlalchemy.ext.asyncio.AsyncSession]:
        async with self._session_factory() as session:
            try:
                logger.debug("Creating database session")
                yield session
            except Exception:
                logger.warning("Rolling back session", exc_info=True)
                await session.rollback()
                raise
            finally:
                logger.debug("Closing database session")
                await session.close()

    # for testing
    async def create_all_schemas_for_testing(
        self,
        meta: sqlalchemy.MetaData,
        drop_all: bool = False,
    ) -> None:
        logger.warning("Creating all schemas for testing")
        async with self._engine.begin() as transaction:
            if self._engine.name == "sqlite":
                # https://docs.sqlalchemy.org/en/14/dialects/sqlite.html#foreign-key-support
                await transaction.execute(text("PRAGMA foreign_keys=ON"))
            if drop_all:
                await transaction.run_sync(meta.drop_all)
            await transaction.run_sync(meta.create_all)
            await transaction.commit()
