from os import environ
from typing import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.security_repository import ISecurityRepository
from app.repository.sa_repository.candle_repo import CandleRepository
from app.repository.sa_repository.security_repo import SecurityRepository


async def connection_factory() -> AsyncGenerator[AsyncConnection]:
    """Get connection."""
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


async def security_repository_provider(
    conn: AsyncConnection = Depends(connection_factory),
) -> AsyncGenerator[ISecurityRepository]:
    """Get Security Repository."""
    yield SecurityRepository(conn)


async def candle_repository_provider(
    conn: AsyncConnection = Depends(connection_factory),
) -> AsyncGenerator[ICandleRepository]:
    """Get Security Repository."""
    yield CandleRepository(conn)
