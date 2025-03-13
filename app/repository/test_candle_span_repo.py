from datetime import timedelta
from uuid import uuid4

from app.core.date_time import Timestamp
from app.core.entities import Security, CandleSpan, Timeframe, Entity
from app.core.unit_of_work import IUnitOfWork
from app.core.repository.base import IRepository, Record
from app.core.repository.security_repository import ISecurityRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository


class TestCases:

    @staticmethod
    async def execute_create_candle_span(
        uow: IUnitOfWork,
        security_repo: ISecurityRepository,
        candle_span_repo: ICandleSpanRepository,
    ):
        test_ticker = uuid4().hex
        test_board = uuid4().hex

        security = Security(ticker=test_ticker, board=test_board)
        candle_span = CandleSpan(
            security=security,
            timeframe=Timeframe.H1,
            date_from=Timestamp("2025-01-01"),
            date_till=Timestamp("2025-01-10"),
        )

        async with uow:

            await security_repo.add([security])
            await candle_span_repo.add([candle_span])

            candle_span_repo = candle_span_repo.filter_by_security(security)
            count = await candle_span_repo.count()
            assert count == 1

            candle_span_records = [r async for r in candle_span_repo]
            await candle_span_repo.remove(candle_span_records)

            count = await candle_span_repo.count()
            assert count == 0

            security_records = [
                r async for r in security_repo.filter_by_ticker(test_ticker)
            ]
            await security_repo.remove(security_records)
            count = await security_repo.filter_by_ticker(test_ticker).count()
            assert count == 0

    @staticmethod
    async def execute_create_many_candle_spans(
        uow: IUnitOfWork,
        security_repo: ISecurityRepository,
        candle_span_repo: ICandleSpanRepository,
    ):

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

        async with uow:

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

            security_records = [
                r async for r in security_repo.filter_by_ticker(test_ticker)
            ]
            await security_repo.remove(security_records)
            count = await security_repo.filter_by_ticker(test_ticker).count()
            assert count == 0

    @staticmethod
    async def execute_slicing(
        uow: IUnitOfWork,
        security_repo: ISecurityRepository,
        candle_span_repo: ICandleSpanRepository,
    ):

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

        async with uow:

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

            security_records = [
                r async for r in security_repo.filter_by_ticker(test_ticker)
            ]
            await security_repo.remove(security_records)
            count = await security_repo.filter_by_ticker(test_ticker).count()
            assert count == 0

    @staticmethod
    async def execute_candle_span_filters(
        uow: IUnitOfWork,
        security_repo: ISecurityRepository,
        candle_span_repo: ICandleSpanRepository,
    ):

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

        async with uow:

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

                security_records = [
                    r async for r in security_repo.filter_by_ticker(security.ticker)
                ]
                await security_repo.remove(security_records)
                await _check_count(security_repo.filter_by_ticker(security.ticker), 0)
