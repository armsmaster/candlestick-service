from fastapi import APIRouter, Depends, Request

from app.core.logger import ILogger
from app.core.repository.security_repository import ISecurityRepository
from app.io.rest_api.api.v1.security.schemas import SecuritySchema
from app.io.rest_api.dependency import logger_provider, security_repository_provider
from app.use_cases.get_securities import GetSecurities, GetSecuritiesRequest

router = APIRouter(prefix="/securities")


@router.get("/")
async def get_securities(
    request: Request,
    ticker: str = None,
    board: str = None,
    security_repository: ISecurityRepository = Depends(security_repository_provider),
    logger: ILogger = Depends(logger_provider),
) -> list[SecuritySchema]:
    logger.info(
        "rest_api_request",
        handle="get_securities",
        path=request.url.path,
        param_ticker=ticker,
        param_board=board,
    )
    use_case = GetSecurities(security_repository)
    use_case_request = GetSecuritiesRequest(ticker=ticker, board=board)
    use_case_response = await use_case.execute(use_case_request)
    securities = use_case_response.result
    return [SecuritySchema(**sec.__dict__) for sec in securities]
