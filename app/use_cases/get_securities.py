from dataclasses import dataclass, field

from app.core.entities import Security
from app.core.repository import ISecurityRepository
from app.use_cases.base import (
    BaseUseCase,
    UseCaseRequest,
    UseCaseResponse,
)


@dataclass
class GetSecuritiesRequest(UseCaseRequest):
    """GetSecurities Request."""

    ticker: str = None
    board: str = None


@dataclass
class GetSecuritiesResponse(UseCaseResponse):
    """GetSecurities Response."""

    result: list[Security] | None = None
    errors: list[str] = field(default_factory=list)


class GetSecurities(BaseUseCase):
    """GetSecurities use case."""

    def __init__(
        self,
        security_repo: ISecurityRepository,
    ):
        """Initialize."""
        self.security_repo = security_repo

    async def execute(self, request: GetSecuritiesRequest) -> GetSecuritiesResponse:
        """Execute."""
        repo = self.security_repo
        if request.ticker:
            repo = repo.filter_by_ticker(ticker=request.ticker)
        if request.board:
            repo = repo.filter_by_board(board=request.board)
        securities = [sec async for sec in repo]
        response = GetSecuritiesResponse(result=securities)
        return response
