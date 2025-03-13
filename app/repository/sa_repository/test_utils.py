from os import environ
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection

from app.core.unit_of_work import IUnitOfWork
from app.core.repository.security_repository import ISecurityRepository
from app.repository.sa_repository.security_repo import SecurityRepository

from app.core.repository.candle_repository import ICandleRepository
from app.repository.sa_repository.candle_repo import CandleRepository

from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.repository.sa_repository.candle_span_repo import CandleSpanRepository


class UOW(IUnitOfWork):

    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, traceback) -> bool:
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    async def commit(self):
        await self.connection.commit()

    async def rollback(self):
        await self.connection.rollback()


@asynccontextmanager
async def connection_factory():
    url = "{drivername}://{username}:{password}@{host}:{port}/{database}".format(
        drivername=environ.get("DB_DRIVER"),
        username=environ.get("POSTGRES_USER"),
        password=environ.get("POSTGRES_PASSWORD"),
        host=environ.get("PG_HOST"),
        port=environ.get("PG_PORT"),
        database=environ.get("POSTGRES_DB"),
    )
    engine: AsyncEngine = create_async_engine(url, echo=False)
    try:
        async with engine.connect() as connection:
            yield connection
    finally:
        await engine.dispose()


def security_repository_factory(
    connection: AsyncConnection,
) -> ISecurityRepository:
    return SecurityRepository(connection)


def candle_repository_factory(
    connection: AsyncConnection,
) -> ICandleRepository:
    return CandleRepository(connection)


def candle_span_repository_factory(
    connection: AsyncConnection,
) -> ICandleSpanRepository:
    return CandleSpanRepository(connection)
