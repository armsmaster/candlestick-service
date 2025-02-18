from datetime import datetime
import uuid

from sqlalchemy import ForeignKey, Index
from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncAttrs

from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship


class Base(AsyncAttrs, DeclarativeBase):
    pass


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


Index(
    "idx_candle_unique",
    Candle.security_id,
    Candle.timeframe,
    Candle.timestamp,
    unique=True,
)
