from os import environ
import asyncio
import pytest
from datetime import timedelta
from uuid import uuid4

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncConnection

from app.core.date_time import Timestamp
from app.core.entities import Security, CandleSpan, Timeframe
from app.core.repository.security_repository import ISecurityRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.repository.security_repo import SecurityRepository
from app.repository.candle_span_repo import CandleSpanRepository


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


async def test_create_many_candles(connections=connection_factory()):
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


# async def test_slicing(connections=connection_factory()):
#     connection = await anext(connections)
#     test_ticker = uuid4().hex
#     test_board = uuid4().hex
#     security = Security(
#         ticker=test_ticker,
#         board=test_board,
#     )

#     now = Timestamp.now()
#     candles = [
#         Candle(
#             security=security,
#             timeframe=Timeframe.H1,
#             timestamp=Timestamp(now.dt - timedelta(minutes=i)),
#             open=100,
#             high=101.0,
#             low=99.9,
#             close=100.25,
#         )
#         for i in range(1000)
#     ]

#     async with UOW(connection):
#         security_repo = security_repository_factory(connection)
#         candle_repo = candle_span_repository_factory(connection)

#         await security_repo.add([security])
#         await candle_repo.add(candles)

#         candle_repo = candle_repo.filter_by_security(security)
#         count = await candle_repo.count()
#         assert count == 1000

#         retrieved_candles = []
#         i, batch_size = 0, 100
#         while True:
#             batch_repo = candle_repo[i, i + batch_size]
#             items = [r.entity async for r in batch_repo]
#             retrieved_candles += items
#             if not items:
#                 break
#             i += batch_size

#         assert set(candles) == set(retrieved_candles)

#         records = [r async for r in candle_repo]
#         await candle_repo.remove(records)

#         count = await candle_repo.count()
#         assert count == 0

#         security_repo = security_repo.filter_by_ticker(test_ticker)
#         security_records = [r async for r in security_repo]
#         await security_repo.remove(security_records)
#         count = await security_repo.count()
#         assert count == 0
