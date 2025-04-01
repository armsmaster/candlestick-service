import pytest

from app.dependency.test import Container
from app.repository.test_security_repo import TestCases

dependencies = Container()


class TestSecurityRepoJson:

    @pytest.mark.asyncio
    async def test_create_security(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, _ = elements
            await TestCases.execute_create_security(
                uow,
                security_repo,
            )

    @pytest.mark.asyncio
    async def test_create_many_securities(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, _ = elements
            await TestCases.execute_create_many_securities(
                uow,
                security_repo,
            )

    @pytest.mark.asyncio
    async def test_slicing(self):
        async with dependencies.get_repos() as elements:
            uow, security_repo, _, _ = elements
            await TestCases.execute_slicing(
                uow,
                security_repo,
            )
