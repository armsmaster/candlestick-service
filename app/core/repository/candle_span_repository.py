from abc import ABC, abstractmethod

from app.core.date_time import Timestamp
from app.core.entities import Timeframe
from app.core.entities import Security

from app.core.repository.base import IRepository


class ICandleSpanRepository(IRepository, ABC):

    @abstractmethod
    def filter_by_security(self, security: Security) -> "ICandleSpanRepository":
        raise NotImplementedError

    @abstractmethod
    def filter_by_timeframe(self, timeframe: Timeframe) -> "ICandleSpanRepository":
        raise NotImplementedError
