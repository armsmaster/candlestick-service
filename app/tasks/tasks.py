from app.dependency.prod import Container
from app.exceptions import DatabaseException, MarketDataSourceException
from app.tasks.broker import broker
from app.use_cases.update_candles import UpdateCandles, UpdateCandlesRequest

dependencies = Container()


@broker.task(schedule=[{"cron": "*/10 * * * *"}])
async def update_candles(logger=dependencies.get_logger()):
    """Update Candles Task."""
    logger.bind(task="update_candles")
    logger.info("task_started")
    use_case = UpdateCandles(
        load_candles_provider=dependencies.get_load_candles_use_case,
        security_repo_provider=dependencies.get_security_repository,
        logger=dependencies.get_logger(),
    )
    try:
        await use_case.execute(UpdateCandlesRequest())
    except DatabaseException as e:
        logger.error("error", exception=str(e))
    except MarketDataSourceException as e:
        logger.error("error", exception=str(e))
    logger.info("task_finished")
