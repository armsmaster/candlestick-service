"""Tests for Market Data Loader."""

from uuid import uuid4

import pytest

from app.core.date_time import Timestamp
from app.core.entities import Security, Timeframe
from app.core.market_data_loader import IMarketDataLoader, MarketDataLoaderRequest
from app.core.repository import (
    ICandleRepository,
    ICandleSpanRepository,
    IRepository,
    ISecurityRepository,
)
from app.dependency.test import Container, FakeMarketDataAdapter
from app.market_data_loader import MarketDataLoader

dependencies = Container()


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
            async for rec in candle_repo.filter_by_security(security=security_record)
        ]
        await candle_repo.remove(candle_records)

        candle_span_records = [
            rec
            async for rec in candle_span_repo.filter_by_security(
                security=security_record
            )
        ]
        await candle_span_repo.remove(items=candle_span_records)

        await TestCases._check_count(
            repo=security_repo.filter_by_ticker(ticker),
            expected_count=0,
        )
        await TestCases._check_count(
            repo=candle_repo.filter_by_security(security=security_record),
            expected_count=0,
        )
        await TestCases._check_count(
            repo=candle_span_repo.filter_by_security(security=security_record),
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
        for cs, tfrom, ttill in zip(
            candle_span_records,
            [Timestamp("2025-01-01")],
            [Timestamp("2025-02-28")],
        ):
            assert cs.security == security
            assert cs.timeframe == test_tf
            assert cs.date_from == tfrom
            assert cs.date_till == ttill

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
        for cs, tfrom, ttill in zip(
            candle_span_records,
            [Timestamp("2025-01-01"), Timestamp("2025-02-02")],
            [Timestamp("2025-01-31"), Timestamp("2025-02-28")],
        ):
            assert cs.security == security
            assert cs.timeframe == test_tf
            assert cs.date_from == tfrom
            assert cs.date_till == ttill

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
        async with (
            dependencies.get_security_repository() as security_repository,
            dependencies.get_candle_repository() as candle_repository,
            dependencies.get_candle_span_repository() as candle_span_repository,
            dependencies.get_market_data_adapter() as market_data_adapter,
            dependencies.get_unit_of_work() as uow,
        ):
            market_data_loader = MarketDataLoader(
                market_data_adapter=market_data_adapter,
                security_repository=security_repository,
                candle_repository=candle_repository,
                candle_span_repository=candle_span_repository,
                unit_of_work=uow,
                logger=dependencies.get_logger(),
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
        async with (
            dependencies.get_security_repository() as security_repository,
            dependencies.get_candle_repository() as candle_repository,
            dependencies.get_candle_span_repository() as candle_span_repository,
            dependencies.get_market_data_adapter() as market_data_adapter,
            dependencies.get_unit_of_work() as uow,
        ):

            market_data_loader = MarketDataLoader(
                market_data_adapter=market_data_adapter,
                security_repository=security_repository,
                candle_repository=candle_repository,
                candle_span_repository=candle_span_repository,
                unit_of_work=uow,
                logger=dependencies.get_logger(),
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
        async with (
            dependencies.get_security_repository() as security_repository,
            dependencies.get_candle_repository() as candle_repository,
            dependencies.get_candle_span_repository() as candle_span_repository,
            dependencies.get_market_data_adapter() as market_data_adapter,
            dependencies.get_unit_of_work() as uow,
        ):
            market_data_loader = MarketDataLoader(
                market_data_adapter=market_data_adapter,
                security_repository=security_repository,
                candle_repository=candle_repository,
                candle_span_repository=candle_span_repository,
                unit_of_work=uow,
                logger=dependencies.get_logger(),
            )
            await TestCases.case_load_two_non_overlapping_periods(
                market_data_loader=market_data_loader,
                security_repo=security_repository,
                candle_repo=candle_repository,
                candle_span_repo=candle_span_repository,
            )
