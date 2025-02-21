from uuid import uuid4
from sqlalchemy import insert, select, delete, and_, or_

from app.core.entities import Security
from app.core.repository import ISecurityRepository

from app.repository.base_repo import BaseRepository
from app.repository.metadata import security_table


class SecurityRepository(BaseRepository, ISecurityRepository):

    def create(self, items: list[Security]):
        filter = self.__construct_filter(items)
        existing_set = set(self.select_entities(filter=filter))

        items_to_insert = [item for item in items if item not in existing_set]
        if not items_to_insert:
            return

        insert_stmt = insert(security_table)
        items_to_insert = [
            {"id": uuid4(), "ticker": item.ticker, "board": item.board}
            for item in items_to_insert
        ]
        self.connection.execute(insert_stmt, items_to_insert)
        return

    def update(self, items: list[Security]):
        """Not Implemented"""
        raise NotImplementedError

    def delete(self, items: list[Security]):
        filter = self.__construct_filter(items)
        delete_stmt = delete(security_table).where(filter)
        self.connection.execute(delete_stmt)

    def all(self) -> list[Security]:
        return self.select_entities()

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

    def select_entities(self, filter=None) -> list[Security]:
        where_clause = filter if filter is not None else 1 == 1
        existing_stmt = select(security_table.c["ticker", "board"]).where(where_clause)
        return {
            Security(ticker=ticker, board=board)
            for ticker, board in self.connection.execute(existing_stmt)
        }
