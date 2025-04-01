"""CLI commands."""

from app.dependency.prod import Container
from app.use_cases.create_security import CreateSecurityRequest
from app.use_cases.update_candles import UpdateCandles, UpdateCandlesRequest

dependencies = Container()

logger = dependencies.get_logger()


async def create_security_command(ticker: str, board: str):
    """Create Security Command."""
    logger.debug("create_security_command", ticker=ticker, board=board)
    async with dependencies.get_create_security_use_case() as use_case:
        request = CreateSecurityRequest(ticker=ticker, board=board)
        await use_case.execute(request)


async def update_candles_command():
    """Update Candles Command."""
    logger.debug("update_candles_command")
    use_case = UpdateCandles(
        load_candles_provider=dependencies.get_load_candles_use_case,
        security_repo_provider=dependencies.get_security_repository,
    )
    await use_case.execute(UpdateCandlesRequest())
