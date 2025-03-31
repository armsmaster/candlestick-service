from datetime import datetime

import pytz
from fastapi import APIRouter, Depends

from app.core.date_time import Timestamp
from app.core.entities import Timeframe
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.security_repository import ISecurityRepository
from app.io.rest_api.api.v1.candle.schemas import CandleSchema
from app.io.rest_api.dependency import (
    candle_repository_provider,
    security_repository_provider,
)
from app.use_cases.get_candles import GetCandles, GetCandlesRequest

router = APIRouter(prefix="/candles")


@router.get("/")
async def get_candles(
    ticker: str,
    board: str,
    timeframe: Timeframe,
    time_from: datetime,
    time_till: datetime,
    security_repository: ISecurityRepository = Depends(security_repository_provider),
    candle_repository: ICandleRepository = Depends(candle_repository_provider),
) -> list[CandleSchema]:
    time_from = time_from.astimezone(pytz.UTC)
    time_till = time_till.astimezone(pytz.UTC)
    request = GetCandlesRequest(
        ticker=ticker,
        board=board,
        timeframe=timeframe,
        time_from=Timestamp(time_from),
        time_till=Timestamp(time_till),
    )
    use_case = GetCandles(
        security_repo=security_repository, candle_repo=candle_repository
    )
    response = await use_case.execute(request)
    candles = [
        CandleSchema(
            id=candle.id,
            ticker=candle.security.ticker,
            board=candle.security.board,
            timeframe=candle.timeframe,
            timestamp=candle.timestamp.dt,
            open=candle.open,
            high=candle.high,
            low=candle.low,
            close=candle.close,
        )
        for candle in response.result
    ]
    return candles
