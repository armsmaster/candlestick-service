"""Test cases for SA Candle Span Repository."""

import pytest

from app.dependency.prod import Container
from app.repository.test_candle_span_repo import TestCases

dependencies = Container()


class TestCandleSpanRepoAlchemy:
    """Test cases."""

    @pytest.mark.asyncio
    async def test_create(self):
        """Create candle span."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, candle_span_repo = elements
            await TestCases.execute_create_candle_span(
                uow,
                security_repo,
                candle_span_repo,
            )

    @pytest.mark.asyncio
    async def test_create_many(self):
        """Create many candle spans."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, candle_span_repo = elements
            await TestCases.execute_create_many_candle_spans(
                uow,
                security_repo,
                candle_span_repo,
            )

    @pytest.mark.asyncio
    async def test_slicing(self):
        """Test slicing."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, candle_span_repo = elements
            await TestCases.execute_slicing(
                uow,
                security_repo,
                candle_span_repo,
            )

    @pytest.mark.asyncio
    async def test_filters(self):
        """Test filters."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, candle_span_repo = elements
            await TestCases.execute_candle_span_filters(
                uow,
                security_repo,
                candle_span_repo,
            )
