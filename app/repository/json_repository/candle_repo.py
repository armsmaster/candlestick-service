from typing import override
from uuid import UUID

from app.core.date_time import Timestamp
from app.core.entities import Candle, Security, Timeframe
from app.core.repository import ICandleRepository
from app.repository.json_repository.base_repo import BaseRepository
from app.repository.json_repository.security_repo import SecurityRepository


class CandleRepository(BaseRepository, ICandleRepository):

    @override
    def __init__(
        self,
        repo: BaseRepository | None = None,
    ):
        self._securities: dict[Security, UUID] = {}
        super().__init__()
        self._load_rows("candle.json")
        self._order_by = ["timestamp"] if repo is None else list(repo._order_by)
        if repo is not None:
            self._rows = list(repo._rows)

    @override
    def _row_to_entity(self, row: dict) -> Candle:
        record = Candle(
            id=UUID(row["id"]),
            security=Security(
                id=UUID(row["security_id"]),
                ticker=row["security__ticker"],
                board=row["security__board"],
            ),
            timeframe=Timeframe(row["timeframe"]),
            timestamp=Timestamp(row["timestamp"]),
            open=row["open"],
            high=row["high"],
            low=row["low"],
            close=row["close"],
        )
        return record

    async def _entity_to_row(self, entity: Candle) -> dict:
        return {
            "id": str(entity.id),
            "security_id": str(entity.security.id),
            "security__ticker": entity.security.ticker,
            "security__board": entity.security.board,
            "timeframe": entity.timeframe.value,
            "timestamp": str(entity.timestamp),
            "open": entity.open,
            "high": entity.high,
            "low": entity.low,
            "close": entity.close,
        }

    @override
    async def add(self, items: list[Candle]) -> None:
        if len(items) == 0:
            return

        unique_tuple = lambda r: (r["security_id"], r["timeframe"], r["timestamp"])
        idx = lambda rows: [unique_tuple(r) for r in rows]
        not_dublicate = lambda r, rows: unique_tuple(r) not in idx(rows)

        items_to_insert = [await self._entity_to_row(item) for item in items]
        items_to_insert = [i for i in items_to_insert if not_dublicate(i, self._rows)]
        self._rows += items_to_insert
        self._sort()

        repo = CandleRepository()
        repo._rows += [i for i in items_to_insert if not_dublicate(i, repo._rows)]
        repo._dump_rows("candle.json")

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
    async def remove(self, items: list[Candle]):
        items_ids = [str(i.id) for i in items]
        self._rows = [r for r in self._rows if r["id"] not in items_ids]
        repo = CandleRepository()
        repo._rows = [r for r in repo._rows if r["id"] not in items_ids]
        repo._dump_rows("candle.json")

    @override
    def __getitem__(self, s):
        sl = slice(*s)

        if sl.step is not None:
            raise NotImplementedError(f"step={sl.step}")

        repo = CandleRepository(repo=self)
        repo._rows = repo._rows[sl]
        return repo

    @override
    def filter_by_security(self, security: Security):
        filter1 = lambda a, b: a["security__ticker"] == str(b.ticker)
        filter2 = lambda a, b: a["security__board"] == str(b.board)
        repo = CandleRepository(repo=self)
        rows = [r for r in self._rows if filter1(r, security) and filter2(r, security)]
        repo._rows = rows
        return repo

    @override
    def filter_by_timeframe(self, timeframe):
        filter = lambda a, b: a["timeframe"] == b.value
        repo = CandleRepository(repo=self)
        rows = [r for r in self._rows if filter(r, timeframe)]
        repo._rows = rows
        return repo

    @override
    def filter_by_timestamp_gte(self, timestamp):
        filter = lambda a, b: Timestamp(a["timestamp"]).date() >= b.date()
        repo = CandleRepository(repo=self)
        rows = [r for r in self._rows if filter(r, timestamp)]
        repo._rows = rows
        return repo

    @override
    def filter_by_timestamp_lte(self, timestamp):
        filter = lambda a, b: Timestamp(a["timestamp"]).date() <= b.date()
        repo = CandleRepository(repo=self)
        rows = [r for r in self._rows if filter(r, timestamp)]
        repo._rows = rows
        return repo
