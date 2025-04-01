import pytest

from app.dependency.test import Container
from app.repository.test_candle_repo import TestCases

dependencies = Container()


class TestCandleRepoJson:

    @pytest.mark.asyncio
    async def test_create(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, candle_repo, _ = elements

            await TestCases.execute_create_candle(
                uow,
                security_repo,
                candle_repo,
            )

    @pytest.mark.asyncio
    async def test_create_many(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, candle_repo, _ = elements

            await TestCases.execute_create_many_candles(
                uow,
                security_repo,
                candle_repo,
            )

    @pytest.mark.asyncio
    async def test_slicing(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, candle_repo, _ = elements

            await TestCases.execute_slicing(
                uow,
                security_repo,
                candle_repo,
            )

    @pytest.mark.asyncio
    async def test_filters(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, candle_repo, _ = elements

            await TestCases.execute_candle_filters(
                uow,
                security_repo,
                candle_repo,
            )
