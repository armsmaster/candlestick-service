from uuid import uuid4
from sqlalchemy import insert, select, delete, and_, or_

from app.core.entities import Security
from app.core.repository import ISecurityRepository

from app.repository.base_repo import BaseRepository
from app.repository.metadata import security_table


class SecurityRepository(BaseRepository, ISecurityRepository):

    async def create(self, items: list[Security]):
        filter = self.__construct_filter(items)
        entities = await self.select_entities(filter=filter)
        existing_set = set(entities)

        items_to_insert = [item for item in items if item not in existing_set]
        if not items_to_insert:
            return

        insert_stmt = insert(security_table)
        items_to_insert = [
            {"id": uuid4(), "ticker": item.ticker, "board": item.board}
            for item in items_to_insert
        ]
        await self.connection.execute(insert_stmt, items_to_insert)
        return

    def update(self, items: list[Security]):
        """Not Implemented"""
        raise NotImplementedError

    async def delete(self, items: list[Security]):
        filter = self.__construct_filter(items)
        delete_stmt = delete(security_table).where(filter)
        await self.connection.execute(delete_stmt)

    async def all(self) -> list[Security]:
        out = await self.select_entities()
        return out

    def __construct_filter(self, items: list[Security]):
        cols = security_table.c
        ands = [
            and_(
                cols.ticker == item.ticker,
                cols.board == item.board,
            )
            for item in items
        ]
        return or_(*ands)

    async def select_entities(self, filter=None) -> list[Security]:
        where_clause = filter if filter is not None else 1 == 1
        existing_stmt = select(security_table.c["ticker", "board"]).where(where_clause)
        entities = await self.connection.execute(existing_stmt)
        return {Security(ticker=ticker, board=board) for ticker, board in entities}
