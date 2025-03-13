import pytest

from app.repository.sa_repository.test_utils import (
    UOW,
    connection_factory,
    security_repository_factory,
    candle_repository_factory,
)
from app.repository.test_candle_repo import TestCases


class TestCandleRepoAlchemy:

    @pytest.mark.asyncio
    async def test_create(self):
        cf = connection_factory()
        conn = await anext(aiter(cf))
        await TestCases.execute_create_candle(
            UOW(conn),
            security_repository_factory(conn),
            candle_repository_factory(conn),
        )

    @pytest.mark.asyncio
    async def test_create_many(self):
        cf = connection_factory()
        conn = await anext(aiter(cf))
        await TestCases.execute_create_many_candles(
            UOW(conn),
            security_repository_factory(conn),
            candle_repository_factory(conn),
        )

    @pytest.mark.asyncio
    async def test_slicing(self):
        cf = connection_factory()
        conn = await anext(aiter(cf))
        await TestCases.execute_slicing(
            UOW(conn),
            security_repository_factory(conn),
            candle_repository_factory(conn),
        )

    @pytest.mark.asyncio
    async def test_filters(self):
        cf = connection_factory()
        conn = await anext(aiter(cf))
        await TestCases.execute_candle_filters(
            UOW(conn),
            security_repository_factory(conn),
            candle_repository_factory(conn),
        )
