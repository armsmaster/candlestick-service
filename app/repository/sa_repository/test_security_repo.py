import pytest

from app.repository.sa_repository.test_utils import (
    UOW,
    connection_factory,
    security_repository_factory,
)

from app.repository.test_security_repo import TestCases


class TestSecurityRepoAlchemy:

    @pytest.mark.asyncio
    async def test_create_security(self):
        async with connection_factory() as conn:
            await TestCases.execute_create_security(
                UOW(conn),
                security_repository_factory(conn),
            )

    @pytest.mark.asyncio
    async def test_create_many_securities(self):
        async with connection_factory() as conn:
            await TestCases.execute_create_many_securities(
                UOW(conn),
                security_repository_factory(conn),
            )

    @pytest.mark.asyncio
    async def test_slicing(self):
        async with connection_factory() as conn:
            await TestCases.execute_slicing(
                UOW(conn),
                security_repository_factory(conn),
            )
