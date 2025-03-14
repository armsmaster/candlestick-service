from app.core.unit_of_work import IUnitOfWork

from app.core.repository.security_repository import ISecurityRepository
from app.repository.json_repository.security_repo import SecurityRepository

from app.core.repository.candle_repository import ICandleRepository
from app.repository.json_repository.candle_repo import CandleRepository

from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.repository.json_repository.candle_span_repo import CandleSpanRepository


class UOW(IUnitOfWork):

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


def security_repository_factory() -> ISecurityRepository:
    return SecurityRepository()


def candle_repository_factory() -> ICandleRepository:
    return CandleRepository()


def candle_span_repository_factory() -> ICandleSpanRepository:
    return CandleSpanRepository()
