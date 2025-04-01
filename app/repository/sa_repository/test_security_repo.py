"""Test cases for SA Security Repository."""

import pytest

from app.dependency.prod import Container
from app.repository.test_security_repo import TestCases

dependencies = Container()


class TestSecurityRepoAlchemy:
    """Test cases."""

    @pytest.mark.asyncio
    async def test_create_security(self):
        """Create security."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, _ = elements
            await TestCases.execute_create_security(uow, security_repo)

    @pytest.mark.asyncio
    async def test_create_many_securities(self):
        """Create many securities."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, _ = elements
            await TestCases.execute_create_many_securities(
                uow,
                security_repo,
            )

    @pytest.mark.asyncio
    async def test_slicing(self):
        """Test slicing."""
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, _ = elements
            await TestCases.execute_slicing(
                uow,
                security_repo,
            )
