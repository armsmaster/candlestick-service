import pytest

from uuid import uuid4

from app.core.unit_of_work import IUnitOfWork

from app.core.date_time import Timestamp
from app.core.entities import Security, Timeframe
from app.core.repository.base import IRepository

from app.core.market_data_adapter import IMarketDataAdapter
from app.core.market_data_loader import IMarketDataLoader, MarketDataLoaderRequest

from app.core.repository.security_repository import ISecurityRepository
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository

from app.market_data_loader.market_data_loader import MarketDataLoader

from app.market_data_loader.test_utils import (
    FakeMarketDataAdapter,
    UOW,
    security_repository_factory,
    candle_repository_factory,
    candle_span_repository_factory,
)


class TestCases:

    @staticmethod
    async def _check_count(repo: IRepository, expected_count: int):
        count = await repo.count()
        assert count == expected_count

    @staticmethod
    async def case_load(
        market_data_loader: IMarketDataLoader,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
    ):
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

        sec_to_remove = [r async for r in security_repo.filter_by_ticker(test_ticker)]
        # security_repo.remove(sec_to_remove)
        await TestCases._check_count(security_repo.filter_by_ticker(test_ticker), 1)


class Test:

    @pytest.mark.asyncio
    async def test_load(self):
        market_data_loader = MarketDataLoader(
            market_data_adapter=FakeMarketDataAdapter(),
            security_repository=security_repository_factory(),
            candle_repository=candle_repository_factory(),
            candle_span_repository=candle_span_repository_factory(),
            unit_of_work=UOW(),
        )
        await TestCases.case_load(
            market_data_loader=market_data_loader,
            security_repo=market_data_loader.security_repository,
            candle_repo=market_data_loader.candle_repository,
        )
