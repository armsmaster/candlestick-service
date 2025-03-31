from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class CandleSchema(BaseModel):
    id: UUID
    ticker: str
    board: str
    timeframe: str
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
