from typing import Annotated, AsyncGenerator

from fastapi import Query

from app.core.logger import ILogger
from app.core.repository import ICandleRepository, ISecurityRepository
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


async def pagination_parameters(
    page_number: Annotated[
        int | None,
        Query(
            title="page number",
            description="optional parameter - page number",
            ge=1,
        ),
    ] = 1,
    page_size: Annotated[
        int | None,
        Query(
            title="page size",
            description="optional parameter - page size",
            ge=1,
            le=100,
        ),
    ] = 10,
):
    """Return pagination query parameters."""
    return {"page_number": page_number, "page_size": page_size}
