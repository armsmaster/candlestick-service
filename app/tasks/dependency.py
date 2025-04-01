"""Dependency Injection."""

from contextlib import asynccontextmanager
from os import environ
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncConnection, AsyncEngine, create_async_engine

from app.core.market_data_adapter import IMarketDataAdapter
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.core.repository.security_repository import ISecurityRepository
from app.core.unit_of_work import IUnitOfWork
from app.market_data_adapter.market_data_adapter import MarketDataAdapter
from app.market_data_loader.market_data_loader import MarketDataLoader
from app.repository.sa_repository.candle_repo import CandleRepository
from app.repository.sa_repository.candle_span_repo import CandleSpanRepository
from app.repository.sa_repository.security_repo import SecurityRepository
from app.repository.sa_repository.unit_of_work import UOW
from app.use_cases.load_candles import LoadCandles


@asynccontextmanager
async def connection_factory():
    """Get connection."""
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


def unit_of_work_factory(connection: AsyncConnection) -> IUnitOfWork:
    """Return UOW implementation."""
    return UOW(connection)


def security_repository_factory(
    connection: AsyncConnection,
) -> ISecurityRepository:
    """Get Security Repository."""
    return SecurityRepository(connection)


@asynccontextmanager
async def security_repository_provider() -> AsyncGenerator[ISecurityRepository]:
    """Get Security Repository."""
    async with connection_factory() as conn:
        yield SecurityRepository(conn)


def candle_repository_factory(
    connection: AsyncConnection,
) -> ICandleRepository:
    """Get Candle Repository."""
    return CandleRepository(connection)


def candle_span_repository_factory(
    connection: AsyncConnection,
) -> ICandleSpanRepository:
    """Get Candle Span Repository."""
    return CandleSpanRepository(connection)


def market_data_adapter_factory() -> IMarketDataAdapter:
    """Get Market Data Adapter."""
    return MarketDataAdapter()


@asynccontextmanager
async def load_candles_use_case_provider():
    """Return initialized LoadCandles Use Case."""
    async with connection_factory() as connection:
        market_data_adapter = market_data_adapter_factory()
        uow = unit_of_work_factory(connection)
        security_repo = security_repository_factory(connection)
        candle_repository = candle_repository_factory(connection)
        candle_span_repository = candle_span_repository_factory(connection)

        market_data_loader = MarketDataLoader(
            market_data_adapter=market_data_adapter,
            security_repository=security_repo,
            candle_repository=candle_repository,
            candle_span_repository=candle_span_repository,
            unit_of_work=uow,
        )

        load_candles_use_case = LoadCandles(market_data_loader=market_data_loader)
        yield load_candles_use_case
