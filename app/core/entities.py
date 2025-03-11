from dataclasses import dataclass
from enum import Enum

from app.core.date_time import Timestamp


class Timeframe(Enum):

    M1 = "M1"
    M10 = "M10"
    H1 = "H1"


@dataclass(frozen=True)
class Entity:
    pass


@dataclass(frozen=True)
class Security(Entity):

    ticker: str
    board: str


@dataclass(frozen=True)
class Candle(Entity):

    security: Security
    timeframe: Timeframe
    timestamp: Timestamp
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class CandleSpan(Entity):

    security: Security
    timeframe: Timeframe
    date_from: Timestamp
    date_till: Timestamp
