import pytest

from app.repository.json_repository.test_utils import (
    UOW,
    security_repository_factory,
    candle_repository_factory,
)
from app.repository.test_candle_repo import TestCases


class TestCandleRepoJson:

    @pytest.mark.asyncio
    async def test_create(self):
        await TestCases.execute_create_candle(
            UOW(),
            security_repository_factory(),
            candle_repository_factory(),
        )

    @pytest.mark.asyncio
    async def test_create_many(self):
        await TestCases.execute_create_many_candles(
            UOW(),
            security_repository_factory(),
            candle_repository_factory(),
        )

    @pytest.mark.asyncio
    async def test_slicing(self):
        await TestCases.execute_slicing(
            UOW(),
            security_repository_factory(),
            candle_repository_factory(),
        )

    @pytest.mark.asyncio
    async def test_filters(self):
        await TestCases.execute_candle_filters(
            UOW(),
            security_repository_factory(),
            candle_repository_factory(),
        )
