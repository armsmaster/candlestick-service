"""Test cases for SA Candle Repository."""

import pytest

from app.dependency.prod import Container
from app.repository.test_candle_repo import TestCases

dependencies = Container()


class TestCandleRepoAlchemy:
    """Test cases."""

    @pytest.mark.asyncio
    async def test_create(self):
        """Create candle."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, candle_repo, _ = elements
            await TestCases.execute_create_candle(
                uow,
                security_repo,
                candle_repo,
            )

    @pytest.mark.asyncio
    async def test_create_many(self):
        """Create many candles."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, candle_repo, _ = elements
            await TestCases.execute_create_many_candles(
                uow,
                security_repo,
                candle_repo,
            )

    @pytest.mark.asyncio
    async def test_slicing(self):
        """Test slicing."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, candle_repo, _ = elements
            await TestCases.execute_slicing(
                uow,
                security_repo,
                candle_repo,
            )

    @pytest.mark.asyncio
    async def test_filters(self):
        """Test filters."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, candle_repo, _ = elements
            await TestCases.execute_candle_filters(
                uow,
                security_repo,
                candle_repo,
            )
