from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException, Request

from app.core.logger import ILogger
from app.core.repository import ISecurityRepository
from app.exceptions import DatabaseException
from app.io.rest_api.api.v1.schemas import HTTPErrorSchema
from app.io.rest_api.api.v1.security.schemas import SecuritySchema
from app.io.rest_api.dependency import logger_provider, security_repository_provider
from app.use_cases.get_securities import GetSecurities, GetSecuritiesRequest

router = APIRouter(prefix="/securities", tags=["securities"])


@router.get(
    "/",
    responses={HTTPStatus.INTERNAL_SERVER_ERROR: {"model": HTTPErrorSchema}},
)
async def get_securities(
    request: Request,
    ticker: str = None,
    board: str = None,
    security_repository: ISecurityRepository = Depends(security_repository_provider),
    logger: ILogger = Depends(logger_provider),
) -> list[SecuritySchema]:
    logger.bind(
        handle="get_securities",
        path=request.url.path,
        param_ticker=ticker,
        param_board=board,
    )
    logger.info("rest_api_request")
    use_case = GetSecurities(security_repository)
    use_case_request = GetSecuritiesRequest(ticker=ticker, board=board)
    try:
        use_case_response = await use_case.execute(use_case_request)
    except DatabaseException as e:
        logger.error("error", exception=str(e))
        return HTTPException(HTTPStatus.INTERNAL_SERVER_ERROR, detail=str(e))
    securities = use_case_response.result
    return [SecuritySchema(**sec.__dict__) for sec in securities]
