"""Unit of Work."""

from sqlalchemy.ext.asyncio import AsyncConnection

from app.core.unit_of_work import IUnitOfWork


class UOW(IUnitOfWork):
    """SQL Alchemy Unit of Work."""

    def __init__(self, connection: AsyncConnection):
        """Initialize."""
        self.connection = connection

    async def __aenter__(self):
        """Async entre."""
        pass

    async def __aexit__(self, exc_type, exc_val, traceback) -> bool:
        """Async exit."""
        if exc_type is None:
            await self.commit()
        else:
            await self.rollback()

    async def commit(self):
        """Commit."""
        await self.connection.commit()

    async def rollback(self):
        """Rollback."""
        await self.connection.rollback()
