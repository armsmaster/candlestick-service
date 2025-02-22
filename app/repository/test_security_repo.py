from os import environ
import asyncio
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection

from app.core.entities import Security
from app.repository.security_repo import SecurityRepository


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


async def create_many_securities(prefix: str, connections=connection_factory()):
    connection = await anext(connections)
    securities = [
        Security(ticker=f"{prefix}_{i}", board="TEST_BOARD") for i in range(1000)
    ]
    async with UOW(connection):
        repo = SecurityRepository(connection=connection)
        await repo.create(securities)

    async with UOW(connection):
        repo = SecurityRepository(connection=connection)
        await repo.delete(securities)


@pytest.mark.asyncio
async def test_security_repository(connections=connection_factory()):
    security = Security(ticker="TEST_TICKER", board="TEST_BOARD")
    connection = await anext(connections)

    async with UOW(connection):
        repo = SecurityRepository(connection=connection)
        await repo.create([security])

    async with UOW(connection):
        repo = SecurityRepository(connection=connection)
        all = await repo.all()
        assert security in all

    async with UOW(connection):
        repo = SecurityRepository(connection=connection)
        await repo.delete([security])

    async with UOW(connection):
        repo = SecurityRepository(connection=connection)
        all = await repo.all()
        assert security not in all


@pytest.mark.asyncio
async def test_1000_mono():
    await asyncio.gather(
        create_many_securities("A", connections=connection_factory()),
    )


@pytest.mark.asyncio
async def test_1000_x3_concurrent():
    await asyncio.gather(
        *[
            create_many_securities(
                prefix=f"A{i:02.0f}",
                connections=connection_factory(),
            )
            for i in range(3)
        ]
    )
