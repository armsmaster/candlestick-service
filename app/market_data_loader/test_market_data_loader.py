"""Tests for Market Data Loader."""

from uuid import uuid4

import pytest

from app.core.date_time import Timestamp
from app.core.entities import CandleSpan, Security, Timeframe
from app.core.market_data_loader import IMarketDataLoader, MarketDataLoaderRequest
from app.core.repository.base import IRepository
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.core.repository.security_repository import ISecurityRepository
from app.market_data_loader.market_data_loader import MarketDataLoader
from app.market_data_loader.test_utils import (
    UOW,
    FakeMarketDataAdapter,
    candle_repository_factory,
    candle_span_repository_factory,
    security_repository_factory,
)


class TestCases:
    """Test Cases for IMarketDataLoader (interface)."""

    @staticmethod
    async def _clean_up(
        ticker: str,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
        candle_span_repo: ICandleSpanRepository,
    ) -> None:
        """Delete test data."""
        security_record = [r async for r in security_repo.filter_by_ticker(ticker)][0]
        await security_repo.remove([security_record])

        candle_records = [
            rec
            async for rec in candle_repo.filter_by_security(
                security=security_record.entity
            )
        ]
        await candle_repo.remove(candle_records)

        candle_span_records = [
            rec
            async for rec in candle_span_repo.filter_by_security(
                security=security_record.entity
            )
        ]
        await candle_span_repo.remove(items=candle_span_records)

        await TestCases._check_count(
            repo=security_repo.filter_by_ticker(ticker),
            expected_count=0,
        )
        await TestCases._check_count(
            repo=candle_repo.filter_by_security(security=security_record.entity),
            expected_count=0,
        )
        await TestCases._check_count(
            repo=candle_span_repo.filter_by_security(security=security_record.entity),
            expected_count=0,
        )

    @staticmethod
    async def _check_count(repo: IRepository, expected_count: int):
        """Compare record count actual vs. expected."""
        count = await repo.count()
        assert count == expected_count

    @staticmethod
    async def case_load(
        market_data_loader: IMarketDataLoader,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
        candle_span_repo: ICandleSpanRepository,
    ):
        """Test basic use case."""
        test_ticker = uuid4().hex
        test_board = uuid4().hex
        security = Security(ticker=test_ticker, board=test_board)
        await security_repo.add([security])

        test_tf = Timeframe.H1

        request = MarketDataLoaderRequest(
            security=security,
            timeframe=test_tf,
            time_from=Timestamp("2025-01-01"),
            time_till=Timestamp("2025-01-31"),
        )
        await market_data_loader.load_candles(request)

        await TestCases._check_count(
            repo=candle_repo.filter_by_security(security).filter_by_timeframe(test_tf),
            expected_count=31 * FakeMarketDataAdapter.n_hours,
        )

        await TestCases._clean_up(
            ticker=test_ticker,
            security_repo=security_repo,
            candle_repo=candle_repo,
            candle_span_repo=candle_span_repo,
        )

    @staticmethod
    async def case_load_two_overlapping_periods(
        market_data_loader: IMarketDataLoader,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
        candle_span_repo: ICandleSpanRepository,
    ):
        """
        Load candles for two overlapping periods.

        Should issue requests only for non-overlapping part.
        """
        test_ticker = uuid4().hex
        test_board = uuid4().hex
        test_tf = Timeframe.H1

        security = Security(ticker=test_ticker, board=test_board)
        await security_repo.add([security])

        request = MarketDataLoaderRequest(
            security=security,
            timeframe=test_tf,
            time_from=Timestamp("2025-01-01"),
            time_till=Timestamp("2025-01-31"),
        )
        await market_data_loader.load_candles(request)

        request = MarketDataLoaderRequest(
            security=security,
            timeframe=test_tf,
            time_from=Timestamp("2025-01-15"),
            time_till=Timestamp("2025-02-28"),
        )

        mdl: MarketDataLoader = market_data_loader
        batches = await mdl._construct_batches(request)
        assert len(batches) == 1
        assert batches[0].time_from == Timestamp("2025-02-01")
        assert batches[0].time_till == Timestamp("2025-02-28")

        await market_data_loader.load_candles(request)

        await TestCases._check_count(
            repo=candle_repo.filter_by_security(security).filter_by_timeframe(test_tf),
            expected_count=(31 + 28) * FakeMarketDataAdapter.n_hours,
        )
        candle_span_records = [
            rec async for rec in candle_span_repo.filter_by_security(security=security)
        ]
        assert [r.entity for r in candle_span_records] == [
            CandleSpan(
                security=security,
                timeframe=test_tf,
                date_from=Timestamp("2025-01-01"),
                date_till=Timestamp("2025-02-28"),
            )
        ]

        await TestCases._clean_up(
            ticker=test_ticker,
            security_repo=security_repo,
            candle_repo=candle_repo,
            candle_span_repo=candle_span_repo,
        )

    @staticmethod
    async def case_load_two_non_overlapping_periods(
        market_data_loader: IMarketDataLoader,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
        candle_span_repo: ICandleSpanRepository,
    ):
        """Load candles for two non-overlapping periods."""
        test_ticker = uuid4().hex
        test_board = uuid4().hex
        test_tf = Timeframe.H1

        security = Security(ticker=test_ticker, board=test_board)
        await security_repo.add([security])

        request = MarketDataLoaderRequest(
            security=security,
            timeframe=test_tf,
            time_from=Timestamp("2025-01-01"),
            time_till=Timestamp("2025-01-31"),
        )
        await market_data_loader.load_candles(request)

        request = MarketDataLoaderRequest(
            security=security,
            timeframe=test_tf,
            time_from=Timestamp("2025-02-02"),
            time_till=Timestamp("2025-02-28"),
        )
        await market_data_loader.load_candles(request)

        await TestCases._check_count(
            repo=candle_repo.filter_by_security(security).filter_by_timeframe(test_tf),
            expected_count=(31 + 28 - 1) * FakeMarketDataAdapter.n_hours,
        )
        candle_span_records = [
            rec async for rec in candle_span_repo.filter_by_security(security=security)
        ]
        assert [r.entity for r in candle_span_records] == [
            CandleSpan(
                security=security,
                timeframe=test_tf,
                date_from=Timestamp("2025-01-01"),
                date_till=Timestamp("2025-01-31"),
            ),
            CandleSpan(
                security=security,
                timeframe=test_tf,
                date_from=Timestamp("2025-02-02"),
                date_till=Timestamp("2025-02-28"),
            ),
        ]

        await TestCases._clean_up(
            ticker=test_ticker,
            security_repo=security_repo,
            candle_repo=candle_repo,
            candle_span_repo=candle_span_repo,
        )


class Test:
    """Tests for MarketDataLoader (implementation)."""

    @pytest.mark.asyncio
    async def test_load(self):
        """Test basic use case."""
        security_repository = security_repository_factory()
        candle_repository = candle_repository_factory()
        candle_span_repository = candle_span_repository_factory()

        market_data_loader = MarketDataLoader(
            market_data_adapter=FakeMarketDataAdapter(),
            security_repository=security_repository,
            candle_repository=candle_repository,
            candle_span_repository=candle_span_repository,
            unit_of_work=UOW(),
        )
        await TestCases.case_load(
            market_data_loader=market_data_loader,
            security_repo=security_repository,
            candle_repo=candle_repository,
            candle_span_repo=candle_span_repository,
        )

    @pytest.mark.asyncio
    async def test_load_two_overlapping_periods(self):
        """Load candles for two overlapping periods."""
        security_repository = security_repository_factory()
        candle_repository = candle_repository_factory()
        candle_span_repository = candle_span_repository_factory()

        market_data_loader = MarketDataLoader(
            market_data_adapter=FakeMarketDataAdapter(),
            security_repository=security_repository,
            candle_repository=candle_repository,
            candle_span_repository=candle_span_repository,
            unit_of_work=UOW(),
        )
        await TestCases.case_load_two_overlapping_periods(
            market_data_loader=market_data_loader,
            security_repo=security_repository,
            candle_repo=candle_repository,
            candle_span_repo=candle_span_repository,
        )

    @pytest.mark.asyncio
    async def test_load_two_non_overlapping_periods(self):
        """Load candles for two non-overlapping periods."""
        security_repository = security_repository_factory()
        candle_repository = candle_repository_factory()
        candle_span_repository = candle_span_repository_factory()

        market_data_loader = MarketDataLoader(
            market_data_adapter=FakeMarketDataAdapter(),
            security_repository=security_repository,
            candle_repository=candle_repository,
            candle_span_repository=candle_span_repository,
            unit_of_work=UOW(),
        )
        await TestCases.case_load_two_non_overlapping_periods(
            market_data_loader=market_data_loader,
            security_repo=security_repository,
            candle_repo=candle_repository,
            candle_span_repo=candle_span_repository,
        )
