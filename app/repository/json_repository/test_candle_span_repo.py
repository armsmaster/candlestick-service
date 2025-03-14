import pytest

from app.repository.json_repository.test_utils import (
    UOW,
    security_repository_factory,
    candle_span_repository_factory,
)
from app.repository.test_candle_span_repo import TestCases


class TestCandleSpanRepoAlchemy:

    @pytest.mark.asyncio
    async def test_create(self):
        await TestCases.execute_create_candle_span(
            UOW(),
            security_repository_factory(),
            candle_span_repository_factory(),
        )

    @pytest.mark.asyncio
    async def test_create_many(self):
        await TestCases.execute_create_many_candle_spans(
            UOW(),
            security_repository_factory(),
            candle_span_repository_factory(),
        )

    @pytest.mark.asyncio
    async def test_slicing(self):
        await TestCases.execute_slicing(
            UOW(),
            security_repository_factory(),
            candle_span_repository_factory(),
        )

    @pytest.mark.asyncio
    async def test_filters(self):
        await TestCases.execute_candle_span_filters(
            UOW(),
            security_repository_factory(),
            candle_span_repository_factory(),
        )
