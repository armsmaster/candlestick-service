from typing import AsyncGenerator

from app.core.logger import ILogger
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.security_repository import ISecurityRepository
from app.dependency.prod import Container

dependencies = Container()


async def security_repository_provider() -> AsyncGenerator[ISecurityRepository]:
    """Get Security Repository."""
    async with dependencies.get_security_repository() as security_repository:
        yield security_repository


async def candle_repository_provider() -> AsyncGenerator[ICandleRepository]:
    """Get Security Repository."""
    async with dependencies.get_candle_repository() as candle_repository:
        yield candle_repository


async def logger_provider() -> AsyncGenerator[ILogger]:
    yield dependencies.get_logger()
