from datetime import timedelta
from uuid import uuid4

from app.core.date_time import Timestamp
from app.core.entities import Candle, Entity, Security, Timeframe
from app.core.repository.base import IRepository
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.security_repository import ISecurityRepository
from app.core.unit_of_work import IUnitOfWork


class TestCases:
    @staticmethod
    async def execute_create_candle(
        uow: IUnitOfWork,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
    ):
        test_ticker = uuid4().hex
        test_board = uuid4().hex

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

        async with uow:
            await security_repo.add([security])
            await candle_repo.add([candle])

            candle_repo = candle_repo.filter_by_security(security)
            count = await candle_repo.count()
            assert count == 1

            candle_records = [r async for r in candle_repo]
            await candle_repo.remove(candle_records)

            count = await candle_repo.count()
            assert count == 0

            security_repo_ticker = security_repo.filter_by_ticker(test_ticker)
            security_records = [r async for r in security_repo_ticker]
            await security_repo_ticker.remove(security_records)
            count = await security_repo_ticker.count()
            assert count == 0

    @staticmethod
    async def execute_create_many_candles(
        uow: IUnitOfWork,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
    ):
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

        async with uow:
            await security_repo.add([security])
            await candle_repo.add(candles)

            candle_repo = candle_repo.filter_by_security(security)
            count = await candle_repo.count()
            assert count == 1000

            records = [r async for r in candle_repo]
            assert set([r for r in records]) == set(candles)

            await candle_repo.remove(records)
            candle_repo = candle_repo.filter_by_security(security)
            count = await candle_repo.count()
            assert count == 0

            security_repo_ticker = security_repo.filter_by_ticker(test_ticker)
            security_records = [r async for r in security_repo_ticker]
            await security_repo_ticker.remove(security_records)
            count = await security_repo_ticker.count()
            assert count == 0

    @staticmethod
    async def execute_slicing(
        uow: IUnitOfWork,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
    ):
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

        async with uow:

            await security_repo.add([security])
            await candle_repo.add(candles)

            candle_repo = candle_repo.filter_by_security(security)
            count = await candle_repo.count()
            assert count == 1000

            retrieved_candles = []
            i, batch_size = 0, 100
            while True:
                batch_repo = candle_repo[i, i + batch_size]
                items = [r async for r in batch_repo]
                retrieved_candles += items
                if not items:
                    break
                i += batch_size

            assert set(candles) == set(retrieved_candles)

            records = [r async for r in candle_repo]
            await candle_repo.remove(records)

            count = await candle_repo.count()
            assert count == 0

            security_repo_ticker = security_repo.filter_by_ticker(security.ticker)
            security_records = [r async for r in security_repo_ticker]
            await security_repo.remove(security_records)
            count = await security_repo_ticker.count()
            assert count == 0

    @staticmethod
    async def execute_candle_filters(
        uow: IUnitOfWork,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
    ):

        async def _check_count(repo: IRepository, expected_count: int):
            count = await repo.count()
            assert count == expected_count

        async def _compare_records_and_source_entities(
            records: list[Entity],
            entities: list[Entity],
        ):
            set_entities_from_records = set([r for r in records])
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

        async with uow:

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

                security_repo_ticker = security_repo.filter_by_ticker(security.ticker)
                security_records = [r async for r in security_repo_ticker]
                await security_repo.remove(security_records)
                await _check_count(security_repo_ticker, 0)
