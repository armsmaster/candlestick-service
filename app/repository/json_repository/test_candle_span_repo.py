import pytest

from app.dependency.test import Container
from app.repository.test_candle_span_repo import TestCases

dependencies = Container()


class TestCandleSpanRepoJson:

    @pytest.mark.asyncio
    async def test_create(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, candle_span_repo = elements
            await TestCases.execute_create_candle_span(
                uow,
                security_repo,
                candle_span_repo,
            )

    @pytest.mark.asyncio
    async def test_create_many(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, candle_span_repo = elements
            await TestCases.execute_create_many_candle_spans(
                uow,
                security_repo,
                candle_span_repo,
            )

    @pytest.mark.asyncio
    async def test_slicing(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, candle_span_repo = elements
            await TestCases.execute_slicing(
                uow,
                security_repo,
                candle_span_repo,
            )

    @pytest.mark.asyncio
    async def test_filters(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, candle_span_repo = elements
            await TestCases.execute_candle_span_filters(
                uow,
                security_repo,
                candle_span_repo,
            )
