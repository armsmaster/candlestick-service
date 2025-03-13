from os import environ
import asyncio
import pytest

from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection

from app.core.entities import Security
from app.core.repository.security_repository import ISecurityRepository

from app.repository.sa_repository.security_repo import SecurityRepository


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


def security_repository_factory(connection: AsyncConnection) -> ISecurityRepository:
    return SecurityRepository(connection)


async def test_create_security(connections=connection_factory()):
    test_ticker = uuid4().hex
    test_board = uuid4().hex
    connection = await anext(connections)
    security = Security(ticker=test_ticker, board=test_board)

    async with UOW(connection):
        repo = security_repository_factory(connection)

        await repo.add([security])  # create security
        await repo.add([security])  # try create duplicate

        repo = repo.filter_by_ticker(test_ticker)

        # check only one exists
        count = await repo.count()
        assert count == 1

        # clean up
        records = [r async for r in repo]
        await repo.remove(records)

        # check test record deleted
        count = await repo.count()
        assert count == 0


async def test_create_many_securities(connections=connection_factory()):
    connection = await anext(connections)
    test_board = uuid4().hex
    securities = [
        Security(
            ticker=uuid4().hex,
            board=test_board,
        )
        for _ in range(1000)
    ]
    async with UOW(connection):
        repo = security_repository_factory(connection)
        await repo.add(securities)

        repo = repo.filter_by_board(test_board)
        count = await repo.count()
        assert count == 1000

        records = [r async for r in repo]
        await repo.remove(records)

        count = await repo.count()
        assert count == 0


async def test_slicing(connections=connection_factory()):
    connection = await anext(connections)
    test_board = uuid4().hex
    securities = [
        Security(
            ticker=uuid4().hex,
            board=test_board,
        )
        for _ in range(1000)
    ]
    async with UOW(connection):
        repo = security_repository_factory(connection)
        await repo.add(securities)

        repo = repo.filter_by_board(test_board)

        retrieved_securities = []
        i, batch_size = 0, 100
        while True:
            batch_repo = repo[i, i + batch_size]
            items = [r.entity async for r in batch_repo]
            retrieved_securities += items
            if not items:
                break
            i += batch_size

        assert set(securities) == set(retrieved_securities)

        records = [r async for r in repo]
        await repo.remove(records)

        count = await repo.count()
        assert count == 0
