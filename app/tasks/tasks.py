from app.dependency import get_logger
from app.tasks.broker import broker
from app.tasks.dependency import (
    load_candles_use_case_provider,
    security_repository_provider,
)
from app.use_cases.update_candles import UpdateCandles, UpdateCandlesRequest

logger = get_logger()


@broker.task(schedule=[{"cron": "0 5 * * *"}])
async def update_candles():
    """Update Candles Task."""
    logger.info("task_started", task="update_candles")
    use_case = UpdateCandles(
        load_candles_provider=load_candles_use_case_provider,
        security_repo_provider=security_repository_provider,
    )
    await use_case.execute(UpdateCandlesRequest())
    logger.info("task_finished", task="update_candles")
