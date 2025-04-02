"""Load Candles use case implementation."""

from dataclasses import dataclass, field

from app.core.date_time import Timestamp
from app.core.entities import Security, Timeframe
from app.core.market_data_loader import IMarketDataLoader, MarketDataLoaderRequest
from app.logger.logger import ILogger
from app.use_cases.base import (
    BaseUseCase,
    UseCaseEvent,
    UseCaseRequest,
    UseCaseResponse,
)


@dataclass
class LoadCandlesEvent(UseCaseEvent):
    """LoadCandles Event."""

    security: Security
    timeframe: Timeframe
    time_from: Timestamp
    time_till: Timestamp


@dataclass
class LoadCandlesRequest(UseCaseRequest):
    """LoadCandles Request."""

    security: Security
    timeframe: Timeframe
    time_from: Timestamp
    time_till: Timestamp


@dataclass
class LoadCandlesResponse(UseCaseResponse):
    """LoadCandles Response."""

    result: None = None
    errors: list[str] = field(default_factory=list)


class LoadCandles(BaseUseCase):
    """LoadCandles use case."""

    def __init__(self, market_data_loader: IMarketDataLoader, logger: ILogger):
        """Initialize."""
        self.market_data_loader = market_data_loader
        self.logger = logger

    async def execute(self, request: LoadCandlesRequest) -> LoadCandlesResponse:
        """Execute."""
        security = request.security
        mdl_request = MarketDataLoaderRequest(
            security=security,
            timeframe=request.timeframe,
            time_from=request.time_from,
            time_till=request.time_till,
        )
        await self.market_data_loader.load_candles(mdl_request)
        response = LoadCandlesResponse()
        event = LoadCandlesEvent(
            security=security,
            timeframe=request.timeframe,
            time_from=request.time_from,
            time_till=request.time_till,
        )
        await self.log_event(event=event)
        return response
