from os import environ
import asyncio
import pytest
from datetime import timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection

from app.core.date_time import Timestamp
from app.core.entities import Security, CandleSpan, Timeframe, Entity
from app.core.repository.base import IRepository, Record
from app.core.repository.security_repository import ISecurityRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.repository.sa_repository.security_repo import SecurityRepository
from app.repository.sa_repository.candle_span_repo import CandleSpanRepository


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


def candle_span_repository_factory(
    connection: AsyncConnection,
) -> ICandleSpanRepository:
    return CandleSpanRepository(connection)


async def test_create_candle_span(connections=connection_factory()):
    test_ticker = uuid4().hex
    test_board = uuid4().hex

    connection = await anext(connections)
    security = Security(ticker=test_ticker, board=test_board)
    candle_span = CandleSpan(
        security=security,
        timeframe=Timeframe.H1,
        date_from=Timestamp("2025-01-01"),
        date_till=Timestamp("2025-01-10"),
    )

    async with UOW(connection):
        security_repo = security_repository_factory(connection)
        candle_span_repo = candle_span_repository_factory(connection)

        await security_repo.add([security])
        await candle_span_repo.add([candle_span])

        candle_span_repo = candle_span_repo.filter_by_security(security)
        count = await candle_span_repo.count()
        assert count == 1

        candle_span_records = [r async for r in candle_span_repo]
        await candle_span_repo.remove(candle_span_records)

        count = await candle_span_repo.count()
        assert count == 0

        security_repo = security_repo.filter_by_ticker(test_ticker)
        security_records = [r async for r in security_repo]
        await security_repo.remove(security_records)
        count = await security_repo.count()
        assert count == 0


async def test_create_many_candle_spans(connections=connection_factory()):
    connection = await anext(connections)
    test_ticker = uuid4().hex
    test_board = uuid4().hex
    security = Security(
        ticker=test_ticker,
        board=test_board,
    )

    candle_spans = [
        CandleSpan(
            security=security,
            timeframe=Timeframe.H1,
            date_from=Timestamp("2025-01-01"),
            date_till=Timestamp("2025-01-10"),
        ),
        CandleSpan(
            security=security,
            timeframe=Timeframe.H1,
            date_from=Timestamp("2025-02-01"),
            date_till=Timestamp("2025-02-10"),
        ),
        CandleSpan(
            security=security,
            timeframe=Timeframe.H1,
            date_from=Timestamp("2025-03-01"),
            date_till=Timestamp("2025-03-10"),
        ),
    ]

    async with UOW(connection):
        security_repo = security_repository_factory(connection)
        candle_span_repo = candle_span_repository_factory(connection)

        await security_repo.add([security])
        await candle_span_repo.add(candle_spans)

        candle_span_repo = candle_span_repo.filter_by_security(security)
        count = await candle_span_repo.count()
        assert count == 3

        records = [r async for r in candle_span_repo]
        assert set([r.entity for r in records]) == set(candle_spans)

        await candle_span_repo.remove(records)
        candle_span_repo = candle_span_repo.filter_by_security(security)
        count = await candle_span_repo.count()
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

    t = Timestamp("2023-01-01")
    candle_spans = [
        CandleSpan(
            security=security,
            timeframe=Timeframe.H1,
            date_from=Timestamp(t.dt + timedelta(days=i * 5)),
            date_till=Timestamp(t.dt + timedelta(days=(i + 1) * 5)),
        )
        for i in range(100)
    ]

    async with UOW(connection):
        security_repo = security_repository_factory(connection)
        candle_span_repo = candle_span_repository_factory(connection)

        await security_repo.add([security])
        await candle_span_repo.add(candle_spans)

        candle_span_repo = candle_span_repo.filter_by_security(security)
        count = await candle_span_repo.count()
        assert count == 100

        retrieved_candle_spans = []
        i, batch_size = 0, 10
        while True:
            batch_repo = candle_span_repo[i, i + batch_size]
            items = [r.entity async for r in batch_repo]
            retrieved_candle_spans += items
            if not items:
                break
            i += batch_size

        assert set(candle_spans) == set(retrieved_candle_spans)

        records = [r async for r in candle_span_repo]
        await candle_span_repo.remove(records)

        count = await candle_span_repo.count()
        assert count == 0

        security_repo = security_repo.filter_by_ticker(test_ticker)
        security_records = [r async for r in security_repo]
        await security_repo.remove(security_records)
        count = await security_repo.count()
        assert count == 0


async def test_candle_span_filters(connections=connection_factory()):

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

    t = Timestamp("2025-01-01")
    candle_spans: list[CandleSpan] = []
    for security in [security_1, security_2]:
        for timeframe in [Timeframe.M1, Timeframe.M10]:
            candle_spans += [
                CandleSpan(
                    security=security,
                    timeframe=timeframe,
                    date_from=Timestamp(t.dt + timedelta(days=i * 5)),
                    date_till=Timestamp(t.dt + timedelta(days=(i + 1) * 5)),
                )
                for i in range(5)
            ]

    async with UOW(connection):
        security_repo = security_repository_factory(connection)
        candle_span_repo = candle_span_repository_factory(connection)

        await security_repo.add([security_1, security_2])
        await candle_span_repo.add(candle_spans)

        for security in [security_1, security_2]:
            cs_repo_sec = candle_span_repo.filter_by_security(security)
            await _check_count(cs_repo_sec, 10)

            for timeframe in [Timeframe.M1, Timeframe.M10]:
                repo_tf = cs_repo_sec.filter_by_timeframe(timeframe)
                await _check_count(repo_tf, 5)

            records = [r async for r in cs_repo_sec]
            await _compare_records_and_source_entities(
                records=records,
                entities=[cs for cs in candle_spans if cs.security == security],
            )
            await candle_span_repo.remove(records)

            security_repo = security_repository_factory(connection)
            security_repo = security_repo.filter_by_ticker(security.ticker)
            security_records = [r async for r in security_repo]
            await security_repo.remove(security_records)
            await _check_count(security_repo, 0)
