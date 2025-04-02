"""CLI commands."""

from app.core.logger import ILogger
from app.dependency.prod import Container
from app.use_cases.create_security import CreateSecurityRequest
from app.use_cases.update_candles import UpdateCandles, UpdateCandlesRequest

dependencies = Container()


async def create_security(
    ticker: str,
    board: str,
    logger: ILogger = dependencies.get_logger(),
):
    """Create Security Command."""
    logger.info(
        "command_started",
        command="create_security",
        param_ticker=ticker,
        param_board=board,
    )
    async with dependencies.get_create_security_use_case() as use_case:
        request = CreateSecurityRequest(ticker=ticker, board=board)
        await use_case.execute(request)
    logger.info("command_finished", command="create_security")


async def update_candles(logger: ILogger = dependencies.get_logger()):
    """Update Candles Command."""
    logger.info("command_started", command="update_candles")
    use_case = UpdateCandles(
        load_candles_provider=dependencies.get_load_candles_use_case,
        security_repo_provider=dependencies.get_security_repository,
        logger=logger,
    )
    await use_case.execute(UpdateCandlesRequest())
    logger.info("command_finished", command="update_candles")
