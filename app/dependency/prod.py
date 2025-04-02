"""Dependency resolution."""

from contextlib import asynccontextmanager
from os import environ
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from app.core.logger import ILogger
from app.core.market_data_adapter import IMarketDataAdapter
from app.core.market_data_loader import IMarketDataLoader
from app.core.repository import (
    ICandleRepository,
    ICandleSpanRepository,
    ISecurityRepository,
)
from app.core.unit_of_work import IUnitOfWork
from app.dependency.container import IContainer
from app.logger.logger import StructLogger
from app.market_data_adapter import MarketDataAdapter
from app.market_data_loader import MarketDataLoader
from app.repository.sa_repository import (
    UOW,
    CandleRepository,
    CandleSpanRepository,
    SecurityRepository,
)
from app.use_cases.create_security import CreateSecurity
from app.use_cases.load_candles import LoadCandles


class Container(IContainer):

    def get_logger(self) -> ILogger:
        logger = StructLogger()
        logger.bind(app="candles-app")
        return logger

    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[AsyncConnection]:
        url = "{drivername}://{username}:{password}@{host}:{port}/{database}".format(
            drivername=environ.get("DB_DRIVER"),
            username=environ.get("POSTGRES_USER"),
            password=environ.get("POSTGRES_PASSWORD"),
            host=environ.get("PG_HOST"),
            port=environ.get("PG_PORT"),
            database=environ.get("POSTGRES_DB"),
        )
        engine: AsyncEngine = create_async_engine(url, echo=False)
        try:
            async with engine.connect() as connection:
                yield connection
        finally:
            await engine.dispose()

    @asynccontextmanager
    async def get_unit_of_work(self) -> AsyncGenerator[IUnitOfWork]:
        async with self.get_connection() as conn:
            yield UOW(conn)

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
        async with self.get_connection() as conn:
            yield (
                UOW(conn),
                SecurityRepository(conn),
                CandleRepository(conn),
                CandleSpanRepository(conn),
            )

    @asynccontextmanager
    async def get_security_repository(self) -> AsyncGenerator[ISecurityRepository]:
        async with self.get_connection() as conn:
            yield SecurityRepository(conn)

    @asynccontextmanager
    async def get_candle_repository(self) -> AsyncGenerator[ICandleRepository]:
        async with self.get_connection() as conn:
            yield CandleRepository(conn)

    @asynccontextmanager
    async def get_candle_span_repository(self) -> AsyncGenerator[ICandleSpanRepository]:
        async with self.get_connection() as conn:
            yield CandleSpanRepository(conn)

    @asynccontextmanager
    async def get_market_data_adapter(self) -> AsyncGenerator[IMarketDataAdapter]:
        yield MarketDataAdapter()

    @asynccontextmanager
    async def get_market_data_loader(self) -> AsyncGenerator[IMarketDataLoader]:
        async with self.get_connection() as conn:
            uow = UOW(conn)
            market_data_adapter = MarketDataAdapter()
            security_repository = SecurityRepository(conn)
            candle_repository = CandleRepository(conn)
            candle_span_repository = CandleSpanRepository(conn)
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
        async with self.get_connection() as conn:
            uow = UOW(conn)
            security_repository = SecurityRepository(conn)
            yield CreateSecurity(uow=uow, security_repo=security_repository)
