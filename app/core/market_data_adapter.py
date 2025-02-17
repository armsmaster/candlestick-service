from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.core.date_time import Timestamp
from app.core.entities import Timeframe, Candle


class MarketDataAdapterException(Exception):
    pass


@dataclass
class MarketDataRequest:
    board: str
    ticker: str
    timeframe: Timeframe
    time_from: Timestamp
    time_till: Timestamp


class IMarketDataAdapter(ABC):

    @abstractmethod
    def __init__(self, request: MarketDataRequest):
        pass

    @abstractmethod
    def load(self) -> list[Candle]:
        pass
