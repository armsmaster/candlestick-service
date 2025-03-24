import pytest

from app.repository.json_repository.test_utils import (
    UOW,
    security_repository_factory,
)

from app.repository.test_security_repo import TestCases


class TestSecurityRepoJson:

    @pytest.mark.asyncio
    async def test_create_security(self):
        await TestCases.execute_create_security(
            UOW(),
            security_repository_factory(),
        )

    @pytest.mark.asyncio
    async def test_create_many_securities(self):
        await TestCases.execute_create_many_securities(
            UOW(),
            security_repository_factory(),
        )

    @pytest.mark.asyncio
    async def test_slicing(self):
        await TestCases.execute_slicing(
            UOW(),
            security_repository_factory(),
        )
