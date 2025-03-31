"""Update Candles use case implementation."""

import asyncio
from collections.abc import Callable
from dataclasses import dataclass, field
from itertools import product
from typing import AsyncContextManager

from app.core.date_time import Timestamp
from app.core.entities import Security, Timeframe
from app.core.repository.security_repository import ISecurityRepository
from app.dependency import get_logger
from app.use_cases.base import (
    BaseUseCase,
    UseCaseEvent,
    UseCaseRequest,
    UseCaseResponse,
)
from app.use_cases.load_candles import LoadCandles, LoadCandlesRequest

logger = get_logger()


@dataclass
class UpdateCandlesEvent(UseCaseEvent):
    """UpdateCandles Event."""

    securities: list[Security]


@dataclass
class UpdateCandlesRequest(UseCaseRequest):
    """UpdateCandles Request."""

    time_from: Timestamp = Timestamp("2024-08-01")
    time_till: Timestamp = Timestamp.today() - 1


@dataclass
class UpdateCandlesResponse(UseCaseResponse):
    """UpdateCandles Response."""

    result: None = None
    errors: list[str] = field(default_factory=list)


class UpdateCandles(BaseUseCase):
    """UpdateCandles use case."""

    def __init__(
        self,
        load_candles_provider: Callable[[], AsyncContextManager[LoadCandles]],
        security_repo_provider: Callable[[], AsyncContextManager[ISecurityRepository]],
        n_tasks: int = 5,
    ):
        """Initialize."""
        self.load_candles_provider = load_candles_provider
        self.security_repo_provider = security_repo_provider
        self.n_tasks = n_tasks

    async def execute(self, request: UpdateCandlesRequest) -> UpdateCandlesResponse:
        """Execute."""
        async with self.security_repo_provider() as security_repo:
            securities = [security async for security in security_repo]
        ml_requests = [
            LoadCandlesRequest(
                security=security,
                timeframe=tf,
                time_from=request.time_from,
                time_till=request.time_till,
            )
            for security, tf in product(securities, Timeframe)
        ]
        queue = asyncio.Queue()
        consumers = [
            asyncio.create_task(self._consume(queue)) for _ in range(self.n_tasks)
        ]
        await self._produce(queue, ml_requests)
        await queue.join()
        for consumer in consumers:
            consumer.cancel()

        response = UpdateCandlesResponse()
        event = UpdateCandlesEvent(securities=securities)
        await self.log_event(event=event)
        return response

    async def _consume(self, queue: asyncio.Queue):
        while True:
            request = await queue.get()
            request = request[0]
            logger.debug("UpdateCandles._consume", request=str(request))
            async with self.load_candles_provider() as load_candles_use_case:
                await load_candles_use_case.execute(request)
            queue.task_done()

    async def _produce(self, queue: asyncio.Queue, requests: list[LoadCandlesRequest]):
        for request in requests:
            await queue.put((request,))
        logger.debug("UpdateCandles._produce", tasks_created=len(requests))
