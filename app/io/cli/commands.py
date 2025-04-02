"""CLI commands."""

from app.core.logger import ILogger
from app.dependency.prod import Container
from app.exceptions import DatabaseException, MarketDataSourceException
from app.use_cases.create_security import CreateSecurityRequest
from app.use_cases.update_candles import UpdateCandles, UpdateCandlesRequest

dependencies = Container()


async def create_security(
    ticker: str,
    board: str,
    logger: ILogger = dependencies.get_logger(),
):
    """Create Security Command."""
    logger.bind(
        command="create_security",
        param_ticker=ticker,
        param_board=board,
    )
    logger.info("command_started")
    try:
        async with dependencies.get_create_security_use_case() as use_case:
            request = CreateSecurityRequest(ticker=ticker, board=board)
            await use_case.execute(request)
    except DatabaseException as e:
        logger.error("error", exception=str(e))
    logger.info("command_finished")


async def update_candles(logger: ILogger = dependencies.get_logger()):
    """Update Candles Command."""
    logger.bind(command="update_candles")
    logger.info("command_started")
    try:
        use_case = UpdateCandles(
            load_candles_provider=dependencies.get_load_candles_use_case,
            security_repo_provider=dependencies.get_security_repository,
            logger=dependencies.get_logger(),
        )
        await use_case.execute(UpdateCandlesRequest())
    except DatabaseException as e:
        logger.error("error", exception=str(e))
    except MarketDataSourceException as e:
        logger.error("error", exception=str(e))
    logger.info("command_finished")
