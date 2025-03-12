from os import environ
import asyncio
import pytest
from datetime import timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection

from app.core.date_time import Timestamp
from app.core.entities import Security, Candle, Timeframe, Entity
from app.core.repository.base import IRepository, Record
from app.core.repository.security_repository import ISecurityRepository
from app.core.repository.candle_repository import ICandleRepository
from app.repository.security_repo import SecurityRepository
from app.repository.candle_repo import CandleRepository


class UOW:

    def __init__(self, connection: AsyncConnection):
        self.connection = connection

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, traceback) -> bool:
        if exc_type is None:
            await self.connection.commit()
        else:
            await self.connection.rollback()


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


def candle_repository_factory(connection: AsyncConnection) -> ICandleRepository:
    return CandleRepository(connection)


async def test_create_candle(connections=connection_factory()):
    test_ticker = uuid4().hex
    test_board = uuid4().hex

    connection = await anext(connections)
    security = Security(ticker=test_ticker, board=test_board)
    candle = Candle(
        security=security,
        timeframe=Timeframe.H1,
        timestamp=Timestamp.now("Europe/Moscow"),
        open=100,
        high=101,
        low=99,
        close=100.1,
    )

    async with UOW(connection):
        security_repo = security_repository_factory(connection)
        candle_repo = candle_repository_factory(connection)

        await security_repo.add([security])
        await candle_repo.add([candle])

        candle_repo = candle_repo.filter_by_security(security)
        count = await candle_repo.count()
        assert count == 1

        candle_records = [r async for r in candle_repo]
        await candle_repo.remove(candle_records)

        count = await candle_repo.count()
        assert count == 0

        security_repo = security_repo.filter_by_ticker(test_ticker)
        security_records = [r async for r in security_repo]
        await security_repo.remove(security_records)
        count = await security_repo.count()
        assert count == 0


async def test_create_many_candles(connections=connection_factory()):
    connection = await anext(connections)
    test_ticker = uuid4().hex
    test_board = uuid4().hex
    security = Security(
        ticker=test_ticker,
        board=test_board,
    )

    now = Timestamp.now()
    candles = [
        Candle(
            security=security,
            timeframe=Timeframe.H1,
            timestamp=Timestamp(now.dt - timedelta(minutes=i)),
            open=100,
            high=101.0,
            low=99.9,
            close=100.25,
        )
        for i in range(1000)
    ]

    async with UOW(connection):
        security_repo = security_repository_factory(connection)
        candle_repo = candle_repository_factory(connection)

        await security_repo.add([security])
        await candle_repo.add(candles)

        candle_repo = candle_repo.filter_by_security(security)
        count = await candle_repo.count()
        assert count == 1000

        records = [r async for r in candle_repo]
        assert set([r.entity for r in records]) == set(candles)

        await candle_repo.remove(records)
        candle_repo = candle_repo.filter_by_security(security)
        count = await candle_repo.count()
        assert count == 0

        security_repo = security_repo.filter_by_ticker(test_ticker)
        security_records = [r async for r in security_repo]
        await security_repo.remove(security_records)
        count = await security_repo.count()
        assert count == 0


async def test_slicing(connections=connection_factory()):
    connection = await anext(connections)
    test_ticker = uuid4().hex
    test_board = uuid4().hex
    security = Security(
        ticker=test_ticker,
        board=test_board,
    )

    now = Timestamp.now()
    candles = [
        Candle(
            security=security,
            timeframe=Timeframe.H1,
            timestamp=Timestamp(now.dt - timedelta(minutes=i)),
            open=100,
            high=101.0,
            low=99.9,
            close=100.25,
        )
        for i in range(1000)
    ]

    async with UOW(connection):
        security_repo = security_repository_factory(connection)
        candle_repo = candle_repository_factory(connection)

        await security_repo.add([security])
        await candle_repo.add(candles)

        candle_repo = candle_repo.filter_by_security(security)
        count = await candle_repo.count()
        assert count == 1000

        retrieved_candles = []
        i, batch_size = 0, 100
        while True:
            batch_repo = candle_repo[i, i + batch_size]
            items = [r.entity async for r in batch_repo]
            retrieved_candles += items
            if not items:
                break
            i += batch_size

        assert set(candles) == set(retrieved_candles)

        records = [r async for r in candle_repo]
        await candle_repo.remove(records)

        count = await candle_repo.count()
        assert count == 0

        security_repo = security_repo.filter_by_ticker(test_ticker)
        security_records = [r async for r in security_repo]
        await security_repo.remove(security_records)
        count = await security_repo.count()
        assert count == 0


async def test_candle_filters(connections=connection_factory()):

    async def _check_count(repo: IRepository, expected_count: int):
        count = await repo.count()
        assert count == expected_count

    async def _compare_records_and_source_entities(
        records: list[Record],
        entities: list[Entity],
    ):
        set_entities_from_records = set([r.entity for r in records])
        set_entities = set(entities)
        assert set_entities_from_records == set_entities

    connection = await anext(connections)
    test_ticker_1 = uuid4().hex
    test_ticker_2 = uuid4().hex
    test_board = uuid4().hex
    security_1 = Security(
        ticker=test_ticker_1,
        board=test_board,
    )
    security_2 = Security(
        ticker=test_ticker_2,
        board=test_board,
    )

    t = Timestamp("2025-01-01 12:00:00+03:00")
    candles: list[Candle] = []
    for security in [security_1, security_2]:
        for timeframe in [Timeframe.M1, Timeframe.M10]:
            candles += [
                Candle(
                    security=security,
                    timeframe=timeframe,
                    timestamp=Timestamp(t.dt + timedelta(days=i)),
                    open=100,
                    high=101.0,
                    low=99.9,
                    close=100.25,
                )
                for i in range(60)
            ]

    async with UOW(connection):
        security_repo = security_repository_factory(connection)
        candle_repo = candle_repository_factory(connection)

        await security_repo.add([security_1, security_2])
        await candle_repo.add(candles)

        for security in [security_1, security_2]:
            candle_repo_sec = candle_repo.filter_by_security(security)
            await _check_count(candle_repo_sec, 120)

            for timeframe in [Timeframe.M1, Timeframe.M10]:
                repo_tf = candle_repo_sec.filter_by_timeframe(timeframe)
                await _check_count(repo_tf, 60)

                repo_jan = repo_tf.filter_by_timestamp_gte(
                    Timestamp("2025-01-01 00:00:00")
                ).filter_by_timestamp_lte(Timestamp("2025-01-31 23:59:59"))
                await _check_count(repo_jan, 31)

            records = [r async for r in candle_repo_sec]
            await _compare_records_and_source_entities(
                records=records,
                entities=[c for c in candles if c.security == security],
            )
            await candle_repo.remove(records)

            security_repo = security_repository_factory(connection)
            security_repo = security_repo.filter_by_ticker(security.ticker)
            security_records = [r async for r in security_repo]
            await security_repo.remove(security_records)
            await _check_count(security_repo, 0)
