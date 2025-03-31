from fastapi import APIRouter, Depends

from app.core.repository.security_repository import ISecurityRepository
from app.io.rest_api.api.v1.security.schemas import SecuritySchema
from app.io.rest_api.dependency import security_repository_provider
from app.use_cases.get_securities import GetSecurities, GetSecuritiesRequest

router = APIRouter(prefix="/securities")


@router.get("/")
async def get_securities(
    ticker: str = None,
    board: str = None,
    security_repository: ISecurityRepository = Depends(security_repository_provider),
) -> list[SecuritySchema]:
    use_case = GetSecurities(security_repository)
    request = GetSecuritiesRequest(ticker=ticker, board=board)
    response = await use_case.execute(request)
    securities = response.result
    return [SecuritySchema(**sec.__dict__) for sec in securities]
