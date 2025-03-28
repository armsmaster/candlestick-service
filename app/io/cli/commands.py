"""CLI commands."""

from app.dependency import get_logger
from app.io.cli.dependency import (
    connection_factory,
    load_candles_use_case_provider,
    security_repository_factory,
    security_repository_provider,
    unit_of_work_factory,
)
from app.use_cases.create_security import CreateSecurity, CreateSecurityRequest
from app.use_cases.update_candles import UpdateCandles, UpdateCandlesRequest

logger = get_logger()


async def create_security_command(ticker: str, board: str):
    """Create Security Command."""
    logger.debug("create_security_command", ticker=ticker, board=board)
    async with connection_factory() as conn:
        uow = unit_of_work_factory(conn)
        repo = security_repository_factory(conn)
        request = CreateSecurityRequest(ticker=ticker, board=board)
        use_case = CreateSecurity(uow=uow, security_repo=repo)
        await use_case.execute(request)


async def update_candles_command():
    """Update Candles Command."""
    logger.debug("update_candles_command")
    use_case = UpdateCandles(
        load_candles_provider=load_candles_use_case_provider,
        security_repo_provider=security_repository_provider,
    )
    await use_case.execute(UpdateCandlesRequest())
