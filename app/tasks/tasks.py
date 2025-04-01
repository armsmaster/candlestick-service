from app.dependency.prod import Container
from app.tasks.broker import broker
from app.use_cases.update_candles import UpdateCandles, UpdateCandlesRequest

dependencies = Container()


@broker.task(schedule=[{"cron": "0 5 * * *"}])
async def update_candles(logger=dependencies.get_logger()):
    """Update Candles Task."""
    logger.info("task_started", task="update_candles")
    use_case = UpdateCandles(
        load_candles_provider=dependencies.get_load_candles_use_case,
        security_repo_provider=dependencies.get_security_repository,
    )
    await use_case.execute(UpdateCandlesRequest())
    logger.info("task_finished", task="update_candles")
