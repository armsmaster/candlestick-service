"""Test cases for SA Security Repository."""

import pytest

from app.repository.sa_repository.test_utils import (
    connection_factory,
    security_repository_factory,
)
from app.repository.sa_repository.unit_of_work import UOW
from app.repository.test_security_repo import TestCases


class TestSecurityRepoAlchemy:
    """Test cases."""

    @pytest.mark.asyncio
    async def test_create_security(self):
        """Create security."""
        async with connection_factory() as conn:
            await TestCases.execute_create_security(
                UOW(conn),
                security_repository_factory(conn),
            )

    @pytest.mark.asyncio
    async def test_create_many_securities(self):
        """Create many securities."""
        async with connection_factory() as conn:
            await TestCases.execute_create_many_securities(
                UOW(conn),
                security_repository_factory(conn),
            )

    @pytest.mark.asyncio
    async def test_slicing(self):
        """Test slicing."""
        async with connection_factory() as conn:
            await TestCases.execute_slicing(
                UOW(conn),
                security_repository_factory(conn),
            )
