"""Test cases for SA Candle Repository."""

import pytest

from app.repository.sa_repository.test_utils import (
    candle_repository_factory,
    connection_factory,
    security_repository_factory,
)
from app.repository.sa_repository.unit_of_work import UOW
from app.repository.test_candle_repo import TestCases


class TestCandleRepoAlchemy:
    """Test cases."""

    @pytest.mark.asyncio
    async def test_create(self):
        """Create candle."""
        async with connection_factory() as conn:
            await TestCases.execute_create_candle(
                UOW(conn),
                security_repository_factory(conn),
                candle_repository_factory(conn),
            )

    @pytest.mark.asyncio
    async def test_create_many(self):
        """Create many candles."""
        async with connection_factory() as conn:
            await TestCases.execute_create_many_candles(
                UOW(conn),
                security_repository_factory(conn),
                candle_repository_factory(conn),
            )

    @pytest.mark.asyncio
    async def test_slicing(self):
        """Test slicing."""
        async with connection_factory() as conn:
            await TestCases.execute_slicing(
                UOW(conn),
                security_repository_factory(conn),
                candle_repository_factory(conn),
            )

    @pytest.mark.asyncio
    async def test_filters(self):
        """Test filters."""
        async with connection_factory() as conn:
            await TestCases.execute_candle_filters(
                UOW(conn),
                security_repository_factory(conn),
                candle_repository_factory(conn),
            )
