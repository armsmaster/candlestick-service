"""Dependency resolution."""

from contextlib import asynccontextmanager
from datetime import timedelta
from typing import AsyncGenerator

from app.core.date_time import Timestamp
from app.core.entities import Candle, Timeframe
from app.core.logger import ILogger
from app.core.market_data_adapter import IMarketDataAdapter, MarketDataRequest
from app.core.market_data_loader import IMarketDataLoader
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.core.repository.security_repository import ISecurityRepository
from app.core.unit_of_work import IUnitOfWork
from app.dependency.container import IContainer
from app.logger.logger import StructLogger
from app.market_data_loader.market_data_loader import MarketDataLoader
from app.repository.json_repository.candle_repo import CandleRepository
from app.repository.json_repository.candle_span_repo import CandleSpanRepository
from app.repository.json_repository.security_repo import SecurityRepository
from app.use_cases.create_security import CreateSecurity
from app.use_cases.load_candles import LoadCandles


class FakeUOW(IUnitOfWork):

    def __init__(self):
        pass

    async def __aenter__(self):
        pass

    async def __aexit__(self, exc_type, exc_val, traceback) -> bool:
        pass

    async def commit(self):
        pass

    async def rollback(self):
        pass


class FakeMarketDataAdapter(IMarketDataAdapter):

    n_minutes = 60 * 9
    n_hours = 9

    def __init__(self):
        self._candles: list[Candle] = []

    async def load(self, request: MarketDataRequest):
        self.request = request
        return self._generate_candles()

    def _generate_candles(self) -> list[Candle]:
        t = Timestamp(f"{str(self.request.time_from.date())} 10:00:00+03:00")
        out: list[Candle] = []
        while Timestamp(t.date()) < self.request.time_till + 1:

            candle = Candle(
                security=self.request.security,
                timeframe=self.request.timeframe,
                timestamp=t,
                open=100,
                high=100,
                low=100,
                close=100,
            )
            out.append(candle)

            match self.request.timeframe:
                case Timeframe.M1:
                    t = Timestamp(t.dt + timedelta(minutes=1))
                case Timeframe.M10:
                    t = Timestamp(t.dt + timedelta(minutes=10))
                case Timeframe.H1:
                    t = Timestamp(t.dt + timedelta(minutes=60))

            tmax = Timestamp(f"{str(t.date())} 18:00:00+03:00")
            if t > tmax:
                t = Timestamp(f"{str((t + 1).date())} 10:00:00+03:00")

        return out


class Container(IContainer):

    def get_logger(self) -> ILogger:
        logger = StructLogger()
        logger.bind(app="candles-app")
        return logger

    @asynccontextmanager
    async def get_unit_of_work(self) -> AsyncGenerator[IUnitOfWork]:
        yield FakeUOW()

    @asynccontextmanager
    async def get_repos(
        self,
    ) -> AsyncGenerator[
        tuple[
            IUnitOfWork,
            ISecurityRepository,
            ICandleRepository,
            ICandleSpanRepository,
        ]
    ]:
        yield (
            FakeUOW(),
            SecurityRepository(),
            CandleRepository(),
            CandleSpanRepository(),
        )

    @asynccontextmanager
    async def get_security_repository(self) -> AsyncGenerator[ISecurityRepository]:
        yield SecurityRepository()

    @asynccontextmanager
    async def get_candle_repository(self) -> AsyncGenerator[ICandleRepository]:
        yield CandleRepository()

    @asynccontextmanager
    async def get_candle_span_repository(self) -> AsyncGenerator[ICandleSpanRepository]:
        yield CandleSpanRepository()

    @asynccontextmanager
    async def get_market_data_adapter(self) -> AsyncGenerator[IMarketDataAdapter]:
        yield FakeMarketDataAdapter()

    @asynccontextmanager
    async def get_market_data_loader(self) -> AsyncGenerator[IMarketDataLoader]:
        uow = FakeUOW()
        market_data_adapter = FakeMarketDataAdapter()
        security_repository = SecurityRepository()
        candle_repository = CandleRepository()
        candle_span_repository = CandleSpanRepository()
        yield MarketDataLoader(
            market_data_adapter=market_data_adapter,
            security_repository=security_repository,
            candle_repository=candle_repository,
            candle_span_repository=candle_span_repository,
            unit_of_work=uow,
            logger=self.get_logger(),
        )

    @asynccontextmanager
    async def get_load_candles_use_case(self) -> AsyncGenerator[LoadCandles]:
        async with self.get_market_data_loader() as market_data_loader:
            yield LoadCandles(market_data_loader, logger=self.get_logger())

    @asynccontextmanager
    async def get_create_security_use_case(self) -> AsyncGenerator[CreateSecurity]:
        uow = FakeUOW()
        security_repository = SecurityRepository()
        yield CreateSecurity(uow=uow, security_repo=security_repository)
