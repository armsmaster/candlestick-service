"""Dependencies for test suite."""

from contextlib import asynccontextmanager
from os import environ

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.core.repository.security_repository import ISecurityRepository
from app.repository.sa_repository.candle_repo import CandleRepository
from app.repository.sa_repository.candle_span_repo import CandleSpanRepository
from app.repository.sa_repository.security_repo import SecurityRepository


@asynccontextmanager
async def connection_factory():
    """Yield connection in context."""
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
    """Return security repository."""
    return SecurityRepository(connection)


def candle_repository_factory(
    connection: AsyncConnection,
) -> ICandleRepository:
    """Return candle repository."""
    return CandleRepository(connection)


def candle_span_repository_factory(
    connection: AsyncConnection,
) -> ICandleSpanRepository:
    """Return candle repository."""
    return CandleSpanRepository(connection)
