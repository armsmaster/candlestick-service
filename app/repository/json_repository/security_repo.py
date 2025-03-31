from typing import override
from uuid import UUID

from app.core.entities import Security
from app.core.repository.security_repository import ISecurityRepository
from app.repository.json_repository.base_repo import BaseRepository


class SecurityRepository(BaseRepository, ISecurityRepository):

    @override
    def __init__(
        self,
        repo: BaseRepository | None = None,
    ):
        super().__init__()
        self._order_by = ["ticker", "board"] if repo is None else list(repo._order_by)
        self._load_rows("sec.json")
        if repo is not None:
            self._rows = list(repo._rows)

    @override
    async def count(self) -> int:
        repo = SecurityRepository()
        self._rows = [r for r in repo._rows if r["id"] in [x["id"] for x in self._rows]]
        out = len(self._rows)
        return out

    @override
    def _row_to_entity(self, row: dict) -> Security:
        entity = Security(
            id=UUID(row["id"]),
            ticker=row["ticker"],
            board=row["board"],
        )
        return entity

    async def _entity_to_row(self, entity: Security) -> dict:
        return {
            "id": str(entity.id),
            "ticker": entity.ticker,
            "board": entity.board,
        }

    @override
    async def add(self, items: list[Security]) -> None:
        if len(items) == 0:
            return

        unique_tuple = lambda r: (r["ticker"], r["board"])
        idx = lambda rows: [unique_tuple(r) for r in rows]
        not_dublicate = lambda r, rows: unique_tuple(r) not in idx(rows)

        items_to_insert = [await self._entity_to_row(item) for item in items]
        items_to_insert = [i for i in items_to_insert if not_dublicate(i, self._rows)]
        self._rows += items_to_insert
        self._sort()

        repo = SecurityRepository()
        repo._rows += [i for i in items_to_insert if not_dublicate(i, repo._rows)]
        repo._dump_rows("sec.json")

    @override
    async def remove(self, items: list[Security]):
        items_ids = [str(i.id) for i in items]
        self._rows = [r for r in self._rows if r["id"] not in items_ids]
        repo = SecurityRepository()
        repo._rows = [r for r in repo._rows if r["id"] not in items_ids]
        repo._dump_rows("sec.json")

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
        repo = SecurityRepository()
        rows = [r for r in self._rows if r["board"] == board]
        repo._rows = rows
        return repo

    @override
    def filter_by_ticker(self, ticker):
        repo = SecurityRepository()
        rows = [r for r in self._rows if r["ticker"] == ticker]
        repo._rows = rows
        return repo
