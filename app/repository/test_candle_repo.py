from os import environ
import asyncio
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection

from app.core.date_time import Timestamp
from app.core.entities import Security, Candle, Timeframe
from app.repository.security_repo import SecurityRepository
from app.repository.candle_repo import CandleRepository


class UOW:

    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, traceback) -> bool:
        await self.connection.commit()


async def connection_factory():
    url = "{drivername}://{username}:{password}@{host}:{port}/{database}".format(
        drivername=environ.get("DB_DRIVER"),
        username=environ.get("POSTGRES_USER"),
        password=environ.get("POSTGRES_PASSWORD"),
        host=environ.get("PG_HOST"),
        port=environ.get("PG_PORT"),
        database=environ.get("POSTGRES_DB"),
    )
    try:
        engine: AsyncEngine = create_async_engine(url, echo=False)
        while True:
            async with engine.connect() as connection:
                yield connection
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_candle_repository(connections=connection_factory()):
    security = Security(ticker="T_TICKER", board="T_BOARD")
    candles = [
        Candle(
            security=security,
            timeframe=Timeframe.H1,
            timestamp=Timestamp("2025-02-21 18:50:00"),
            open=100.0,
            high=100.0,
            low=100.0,
            close=100.0,
        )
    ]
    connection = await anext(connections)

    async with UOW(connection):
        repo = SecurityRepository(connection=connection)
        await repo.create([security])

    async with UOW(connection):
        repo = CandleRepository(connection=connection)
        await repo.create(candles)

    # async with UOW(connection):
    #     repo = SecurityRepository(connection=connection)
    #     await repo.delete([security])
