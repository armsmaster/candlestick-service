"""Create Security use case implementation."""

from dataclasses import dataclass, field

from app.core.entities import Security
from app.core.repository.security_repository import ISecurityRepository
from app.core.unit_of_work import IUnitOfWork
from app.use_cases.base import (
    BaseUseCase,
    UseCaseEvent,
    UseCaseRequest,
    UseCaseResponse,
)


@dataclass
class CreateSecurityEvent(UseCaseEvent):
    """CreateSecurity Event."""

    ticker: str
    board: str


@dataclass
class CreateSecurityRequest(UseCaseRequest):
    """CreateSecurity Request."""

    ticker: str
    board: str


@dataclass
class CreateSecurityResponse(UseCaseResponse):
    """CreateSecurity Response."""

    result: Security | None = None
    errors: list[str] = field(default_factory=list)


class CreateSecurity(BaseUseCase):
    """CreateSecurity use case."""

    def __init__(
        self,
        uow: IUnitOfWork,
        security_repo: ISecurityRepository,
    ):
        """Initialize."""
        self.uow = uow
        self.security_repo = security_repo

    async def execute(self, request: CreateSecurityRequest) -> CreateSecurityResponse:
        """Execute."""
        async with self.uow:
            security = Security(ticker=request.ticker, board=request.board)
            await self.security_repo.add([security])
        response = CreateSecurityResponse(result=security)
        event = CreateSecurityEvent(ticker=security.ticker, board=security.board)
        await self.log_event(event=event)
        return response
