from dataclasses import dataclass, field
from enum import Enum
from uuid import UUID, uuid4

from app.core.date_time import Timestamp


class Timeframe(str, Enum):

    M1 = "M1"
    M10 = "M10"
    H1 = "H1"


@dataclass(frozen=True)
class Entity:
    id: UUID = field(default_factory=uuid4)


@dataclass(frozen=True)
class SecurityData:

    ticker: str
    board: str


@dataclass(frozen=True)
class Security(Entity, SecurityData):
    pass


@dataclass(frozen=True)
class CandleData:

    security: Security
    timeframe: Timeframe
    timestamp: Timestamp
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class Candle(Entity, CandleData):
    pass


@dataclass(frozen=True)
class CandleSpanData:

    security: Security
    timeframe: Timeframe
    date_from: Timestamp
    date_till: Timestamp


@dataclass(frozen=True)
class CandleSpan(Entity, CandleSpanData):
    pass
