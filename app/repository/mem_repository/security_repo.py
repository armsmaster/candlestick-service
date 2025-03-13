from typing import override

from uuid import UUID, uuid4

from sqlalchemy import Connection
from sqlalchemy import select, delete, and_, or_, Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Row

from app.core.entities import Security
from app.core.repository.security_repository import ISecurityRepository
from app.core.repository.base import Record

from app.repository.mem_repository.base_repo import BaseRepository


class SecurityRepository(BaseRepository, ISecurityRepository):

    @override
    def __init__(
        self,
        repo: "SecurityRepository" | None = None,
    ):
        super().__init__(
            order_by=["ticker", "board"] if repo is None else list(repo._order_by),
        )
        self._rows = repo._rows

    @override
    def _row_to_record(self, row: dict) -> Record:
        record = Record(
            id=row["id"],
            entity=Security(
                ticker=row["ticker"],
                board=row["board"],
            ),
        )
        return record

    @override
    async def add(self, items: list[Security]) -> None:
        if len(items) == 0:
            return
        items_to_insert = [
            {
                "id": uuid4(),
                "ticker": item.ticker,
                "board": item.board,
            }
            for item in items
        ]
        self._rows += items_to_insert
        for field in reversed(self._order_by):
            self._rows.sort(key=lambda x: x[field])

    @override
    async def remove(self, items: list[Record]):
        self._rows = [r for r in self._rows if r not in items]

    @override
    def __getitem__(self, s):
        sl = slice(*s)

        if sl.step is not None:
            raise NotImplementedError(f"step={sl.step}")

        repo = SecurityRepository(repo=self)
        repo._rows = repo._rows[sl]
        return repo

    @override
    def filter_by_board(self, board):
        repo = SecurityRepository(repo=self)
        repo._rows = [r for r in repo._rows if r["board"] == board]
        return repo

    @override
    def filter_by_ticker(self, ticker):
        repo = SecurityRepository(repo=self)
        repo._rows = [r for r in repo._rows if r["ticker"] == ticker]
        return repo
