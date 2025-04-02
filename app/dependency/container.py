"""Dependency Injection Container Interface."""

from abc import ABC, abstractmethod
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from app.core.logger import ILogger
from app.core.market_data_adapter import IMarketDataAdapter
from app.core.market_data_loader import IMarketDataLoader
from app.core.repository import (
    ICandleRepository,
    ICandleSpanRepository,
    ISecurityRepository,
)
from app.core.unit_of_work import IUnitOfWork
from app.use_cases.create_security import CreateSecurity
from app.use_cases.load_candles import LoadCandles


class IContainer(ABC):

    @abstractmethod
    def get_logger(self) -> ILogger:
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
    async def get_unit_of_work(self) -> AsyncGenerator[IUnitOfWork]:
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
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
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
    async def get_security_repository(self) -> AsyncGenerator[ISecurityRepository]:
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
    async def get_candle_repository(self) -> AsyncGenerator[ICandleRepository]:
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
    async def get_candle_span_repository(self) -> AsyncGenerator[ICandleSpanRepository]:
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
    async def get_market_data_adapter(self) -> AsyncGenerator[IMarketDataAdapter]:
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
    async def get_market_data_loader(self) -> AsyncGenerator[IMarketDataLoader]:
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
    async def get_load_candles_use_case(self) -> AsyncGenerator[LoadCandles]:
        raise NotImplementedError

    @asynccontextmanager
    @abstractmethod
    async def get_create_security_use_case(self) -> AsyncGenerator[CreateSecurity]:
        raise NotImplementedError
