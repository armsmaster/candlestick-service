from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.date_time import Timestamp
from app.core.entities import CandleData, Security, Timeframe


class MarketDataAdapterException(Exception):
    pass


@dataclass
class MarketDataRequest:
    security: Security
    timeframe: Timeframe
    time_from: Timestamp
    time_till: Timestamp


class IMarketDataAdapter(ABC):

    @abstractmethod
    def __init__(self):
        pass

    @abstractmethod
    async def load(self, request: MarketDataRequest) -> list[CandleData]:
        pass
