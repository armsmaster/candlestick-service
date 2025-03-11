from datetime import datetime, date
import uuid

from sqlalchemy import ForeignKey, Index
from sqlalchemy import UUID, BIGINT, TIMESTAMP

# from sqlalchemy.ext.asyncio import AsyncAttrs

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship


class Base(DeclarativeBase):
    type_annotation_map = {
        int: BIGINT,
        datetime: TIMESTAMP(timezone=True),
    }


class Security(Base):
    __tablename__ = "security"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    ticker: Mapped[str]
    board: Mapped[str]


class Candle(Base):
    __tablename__ = "candle"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    security_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("security.id"))
    timeframe: Mapped[str]
    timestamp: Mapped[datetime]
    open: Mapped[float]
    high: Mapped[float]
    low: Mapped[float]
    close: Mapped[float]


class CandleSpan(Base):
    __tablename__ = "candle_span"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True)
    security_id: Mapped[uuid.UUID] = mapped_column(UUID, ForeignKey("security.id"))
    timeframe: Mapped[str]
    date_from: Mapped[date]
    date_till: Mapped[date]


Index(
    "idx_security_unique",
    Security.ticker,
    Security.board,
    unique=True,
)


Index(
    "idx_candle_unique",
    Candle.security_id,
    Candle.timeframe,
    Candle.timestamp,
    unique=True,
)
