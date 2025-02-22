from uuid import uuid4
from sqlalchemy import insert, select, delete, and_, or_, Table

from app.core.entities import Security
from app.core.repository import ISecurityRepository

from app.repository.base_repo import BaseRepository
from app.repository.metadata import security_table


class SecurityRepository(BaseRepository, ISecurityRepository):

    table = security_table
    field_mapping = {
        "ticker": "ticker",
        "board": "board",
    }

    async def create(self, items: list[Security]):
        filter = self._construct_filter(
            items,
            self.table,
            self.field_mapping,
        )
        raw_existing_items = await self._select_raw(
            table=self.table,
            fields=["ticker", "board"],
            filter=filter,
        )
        existing_items = [
            Security(
                ticker=item["ticker"],
                board=item["board"],
            )
            for item in raw_existing_items
        ]
        existing_set = set(existing_items)

        items_to_insert = [item for item in items if item not in existing_set]
        if not items_to_insert:
            return

        insert_stmt = insert(self.table)
        items_to_insert = [
            {"id": uuid4(), "ticker": item.ticker, "board": item.board}
            for item in items_to_insert
        ]
        await self.connection.execute(insert_stmt, items_to_insert)
        return

    async def update(self, items: list[Security]):
        """Not Implemented"""
        raise NotImplementedError

    async def delete(self, items: list[Security]):
        filter = self._construct_filter(
            items,
            self.table,
            self.field_mapping,
        )
        delete_stmt = delete(self.table).where(filter)
        await self.connection.execute(delete_stmt)

    async def all(self) -> list[Security]:
        raw_items = await self._select_raw(table=self.table, fields=["ticker", "board"])
        items = [
            Security(
                ticker=item["ticker"],
                board=item["board"],
            )
            for item in raw_items
        ]
        return items
