from typing import override

from uuid import UUID, uuid4

from sqlalchemy import Connection
from sqlalchemy import select, delete, and_, or_, Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Row

from app.core.entities import Security
from app.core.repository.security_repository import ISecurityRepository
from app.core.repository.base import Record

from app.repository.base_repo import BaseRepository, Filter, FilterGroup
from app.repository.metadata import security_table


class SecurityRepository(BaseRepository, ISecurityRepository):

    table = security_table

    @override
    def __init__(
        self,
        connection: Connection | None = None,
        repo: ISecurityRepository | None = None,
    ):
        super().__init__(
            connection=connection if repo is None else repo._connection,
            table=self.table,
            filters=[] if repo is None else list(repo._filters),
            order_by=["ticker", "board"] if repo is None else list(repo._order_by),
        )

    @override
    def _row_to_record(self, row: Row) -> Record:
        record = Record(
            id=row.id,
            entity=Security(
                ticker=row.ticker,
                board=row.board,
            ),
        )
        return record

    @override
    async def add(self, items: list[Security]) -> None:
        if len(items) == 0:
            return
        insert_stmt = insert(self.table).on_conflict_do_nothing()
        items_to_insert = [
            {
                "id": uuid4(),
                "ticker": item.ticker,
                "board": item.board,
            }
            for item in items
        ]
        await self._connection.execute(insert_stmt, items_to_insert)

    @override
    async def remove(self, items: list[Record]):
        statement = self.table.delete().where(
            or_(False, *[self.table.c["id"] == i.id for i in items])
        )
        await self._connection.execute(statement)

    @override
    def __getitem__(self, s):
        sl = slice(*s)

        if sl.step is not None:
            raise NotImplementedError(f"step={sl.step}")

        repo = SecurityRepository(repo=self)
        repo._limit = sl.stop - sl.start
        repo._offset = sl.start
        return repo

    @override
    def filter_by_board(self, board):
        repo = SecurityRepository(repo=self)
        repo._filters += [self.table.c["board"] == board]
        return repo

    @override
    def filter_by_ticker(self, ticker):
        repo = SecurityRepository(repo=self)
        repo._filters += [self.table.c["ticker"] == ticker]
        return repo
