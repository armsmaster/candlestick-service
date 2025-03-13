from abc import ABC, abstractmethod
from typing import override

from app.core.date_time import Timestamp
from app.core.entities import Timeframe
from app.core.entities import Security, CandleSpan

from app.core.repository.base import IRepository, Record


class ICandleSpanRepository(IRepository):

    @abstractmethod
    def __aiter__(self) -> "ICandleSpanRepository":
        raise NotImplementedError

    @abstractmethod
    async def __anext__(self) -> Record[CandleSpan]:
        raise NotImplementedError

    @abstractmethod
    def filter_by_security(self, security: Security) -> "ICandleSpanRepository":
        raise NotImplementedError

    @abstractmethod
    def filter_by_timeframe(self, timeframe: Timeframe) -> "ICandleSpanRepository":
        raise NotImplementedError
