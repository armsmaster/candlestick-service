from abc import abstractmethod

from app.core.entities import CandleSpan, Security, Timeframe
from app.core.repository.base import IRepository


class ICandleSpanRepository(IRepository):

    @abstractmethod
    def __aiter__(self) -> "ICandleSpanRepository":
        raise NotImplementedError

    @abstractmethod
    async def __anext__(self) -> CandleSpan:
        raise NotImplementedError

    @abstractmethod
    def filter_by_security(self, security: Security) -> "ICandleSpanRepository":
        raise NotImplementedError

    @abstractmethod
    def filter_by_timeframe(self, timeframe: Timeframe) -> "ICandleSpanRepository":
        raise NotImplementedError
