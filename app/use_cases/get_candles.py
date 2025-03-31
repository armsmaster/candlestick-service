from dataclasses import dataclass, field

from app.core.entities import Candle, Security, Timeframe, Timestamp
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.security_repository import ISecurityRepository
from app.use_cases.base import (
    BaseUseCase,
    UseCaseRequest,
    UseCaseResponse,
)


@dataclass
class GetCandlesRequest(UseCaseRequest):
    """GetCandles Request."""

    ticker: str
    board: str
    timeframe: Timeframe
    time_from: Timestamp
    time_till: Timestamp


@dataclass
class GetCandlesResponse(UseCaseResponse):
    """GetCandles Response."""

    result: list[Candle] | None = None
    errors: list[str] = field(default_factory=list)


class GetCandles(BaseUseCase):
    """GetCandles use case."""

    def __init__(
        self,
        security_repo: ISecurityRepository,
        candle_repo: ICandleRepository,
    ):
        """Initialize."""
        self.security_repo = security_repo
        self.candle_repo = candle_repo

    async def execute(self, request: GetCandlesRequest) -> GetCandlesResponse:
        """Execute."""
        security = await self._get_security(request.ticker, request.board)

        repo = self.candle_repo
        repo = repo.filter_by_security(security)
        repo = repo.filter_by_timeframe(request.timeframe)
        repo = repo.filter_by_timestamp_gte(request.time_from)
        repo = repo.filter_by_timestamp_lte(request.time_till)

        candles = [candle async for candle in repo]
        response = GetCandlesResponse(result=candles)
        return response

    async def _get_security(self, ticker: str, board: str) -> Security:
        repo = self.security_repo
        repo = repo.filter_by_board(board)
        repo = repo.filter_by_ticker(ticker)
        securities = [s async for s in repo]
        return securities[0]
