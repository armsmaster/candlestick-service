from datetime import datetime
from http import HTTPStatus

import pytz
from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.date_time import Timestamp
from app.core.entities import Timeframe
from app.core.logger import ILogger
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.security_repository import ISecurityRepository
from app.exceptions import DatabaseException
from app.io.rest_api.api.v1 import HTTPErrorSchema
from app.io.rest_api.api.v1.candle.schemas import CandleSchema
from app.io.rest_api.dependency import (
    candle_repository_provider,
    logger_provider,
    security_repository_provider,
)
from app.use_cases.get_candles import GetCandles, GetCandlesRequest

router = APIRouter(prefix="/candles")


@router.get(
    "/",
    responses={HTTPStatus.INTERNAL_SERVER_ERROR: {"model": HTTPErrorSchema}},
)
async def get_candles(
    request: Request,
    ticker: str,
    board: str,
    timeframe: Timeframe,
    time_from: datetime,
    time_till: datetime,
    security_repository: ISecurityRepository = Depends(security_repository_provider),
    candle_repository: ICandleRepository = Depends(candle_repository_provider),
    logger: ILogger = Depends(logger_provider),
) -> list[CandleSchema]:
    logger.bind(
        handle="get_candles",
        path=request.url.path,
        param_ticker=ticker,
        param_board=board,
        param_timeframe=timeframe,
        param_time_from=time_from,
        param_time_till=time_till,
    )
    logger.info("rest_api_request")
    time_from = time_from.astimezone(pytz.UTC)
    time_till = time_till.astimezone(pytz.UTC)
    use_case_request = GetCandlesRequest(
        ticker=ticker,
        board=board,
        timeframe=timeframe,
        time_from=Timestamp(time_from),
        time_till=Timestamp(time_till),
    )
    use_case = GetCandles(
        security_repo=security_repository, candle_repo=candle_repository
    )
    try:
        use_case_response = await use_case.execute(use_case_request)
    except DatabaseException as e:
        logger.error("error", exception=str(e))
        return HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
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
        for candle in use_case_response.result
    ]
    return candles
