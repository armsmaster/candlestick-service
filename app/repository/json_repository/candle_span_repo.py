from typing import override

from uuid import UUID, uuid4

from sqlalchemy import Connection
from sqlalchemy import select, or_
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Row

from app.core.date_time import Timestamp
from app.core.entities import Security, Timeframe, CandleSpan
from app.core.repository.candle_span_repository import ICandleSpanRepository
from app.core.repository.base import Record

from app.repository.json_repository.base_repo import BaseRepository
from app.repository.json_repository.security_repo import SecurityRepository


class CandleSpanRepository(BaseRepository, ICandleSpanRepository):

    @override
    def __init__(
        self,
        repo: BaseRepository | None = None,
    ):
        self._securities: dict[Security, UUID] = {}
        super().__init__()
        self._load_rows("candle_span.json")
        self._order_by = ["date_from"] if repo is None else list(repo._order_by)
        if repo is not None:
            self._rows = list(repo._rows)

    @override
    def _row_to_record(self, row: dict) -> Record[CandleSpan]:
        record = Record(
            id=row["id"],
            entity=CandleSpan(
                security=Security(
                    ticker=row["security__ticker"],
                    board=row["security__board"],
                ),
                timeframe=Timeframe(row["timeframe"]),
                date_from=Timestamp(row["date_from"]),
                date_till=Timestamp(row["date_till"]),
            ),
        )
        return record

    async def _record_to_row(self, record: CandleSpan) -> dict:
        item = record
        return {
            "id": str(uuid4()),
            "security_id": str(await self._get_security_id(item.security)),
            "security__ticker": item.security.ticker,
            "security__board": item.security.board,
            "timeframe": item.timeframe.value,
            "date_from": str(item.date_from.dt),
            "date_till": str(item.date_till.dt),
        }

    @override
    async def add(self, items: list[CandleSpan]) -> None:
        if len(items) == 0:
            return

        unique_tuple = lambda r: (r["security_id"], r["timeframe"], r["date_from"])
        idx = lambda rows: [unique_tuple(r) for r in rows]
        not_dublicate = lambda r, rows: unique_tuple(r) not in idx(rows)

        items_to_insert = [await self._record_to_row(item) for item in items]
        items_to_insert = [i for i in items_to_insert if not_dublicate(i, self._rows)]
        self._rows += items_to_insert
        self._sort()

        repo = CandleSpanRepository()
        repo._rows += [i for i in items_to_insert if not_dublicate(i, repo._rows)]
        repo._dump_rows("candle_span.json")

    async def _get_security_id(self, security: Security) -> UUID:
        if security in self._securities:
            return self._securities[security]
        security_repo = (
            SecurityRepository()
            .filter_by_board(security.board)
            .filter_by_ticker(security.ticker)
        )
        async for record in security_repo:
            self._securities[security] = record.id
            return record.id

    @override
    async def remove(self, items: list[Record]):
        items_ids = [str(i.id) for i in items]
        self._rows = [r for r in self._rows if r["id"] not in items_ids]
        repo = CandleSpanRepository()
        repo._rows = [r for r in repo._rows if r["id"] not in items_ids]
        repo._dump_rows("candle_span.json")

    @override
    def __getitem__(self, s):
        sl = slice(*s)

        if sl.step is not None:
            raise NotImplementedError(f"step={sl.step}")

        repo = CandleSpanRepository(repo=self)
        repo._rows = repo._rows[sl]
        return repo

    @override
    def filter_by_security(self, security):
        filter1 = lambda a, b: a["security__ticker"] == str(b.ticker)
        filter2 = lambda a, b: a["security__board"] == str(b.board)
        repo = CandleSpanRepository(repo=self)
        rows = [r for r in self._rows if filter1(r, security) and filter2(r, security)]
        repo._rows = rows
        return repo

    @override
    def filter_by_timeframe(self, timeframe):
        filter = lambda a, b: a["timeframe"] == b.value
        repo = CandleSpanRepository(repo=self)
        rows = [r for r in self._rows if filter(r, timeframe)]
        repo._rows = rows
        return repo
