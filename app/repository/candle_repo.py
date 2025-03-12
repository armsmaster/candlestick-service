from typing import override

from uuid import UUID, uuid4

from sqlalchemy import Connection
from sqlalchemy import select, delete, and_, or_, Table
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy import Row

from app.core.date_time import Timestamp
from app.core.entities import Security, Candle, Timeframe
from app.core.repository.candle_repository import ICandleRepository
from app.core.repository.base import Record

from app.repository.base_repo import BaseRepository, Filter, FilterGroup
from app.repository.security_repo import SecurityRepository
from app.repository.metadata import candle_table, security_table


class CandleRepository(BaseRepository, ICandleRepository):

    table = candle_table

    @override
    def __init__(
        self,
        connection: Connection | None = None,
        repo: ICandleRepository | None = None,
    ):
        self._securities: dict[Security, UUID] = {}
        super().__init__(
            connection=connection if repo is None else repo._connection,
            table=self.table,
            filters=[] if repo is None else list(repo._filters),
            order_by=["timestamp"] if repo is None else list(repo._order_by),
        )

    @override
    def _construct_select_base(self):
        return select(self.table, security_table).join(
            security_table,
            security_table.c["id"] == candle_table.c["security_id"],
        )

    @override
    def _row_to_record(self, row: Row) -> Record:
        record = Record(
            id=row.id,
            entity=Candle(
                security=Security(
                    ticker=row.ticker,
                    board=row.board,
                ),
                timeframe=Timeframe(row.timeframe),
                timestamp=Timestamp(row.timestamp),
                open=row.open,
                high=row.high,
                low=row.low,
                close=row.close,
            ),
        )
        return record

    @override
    async def add(self, items: list[Candle]) -> None:
        if len(items) == 0:
            return

        insert_stmt = insert(self.table).on_conflict_do_nothing()
        items_to_insert = [
            {
                "id": uuid4(),
                "security_id": await self._get_security_id(item.security),
                "timeframe": item.timeframe.value,
                "timestamp": item.timestamp.dt,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
            }
            for item in items
        ]
        await self._connection.execute(insert_stmt, items_to_insert)

    async def _get_security_id(self, security: Security) -> UUID:
        if security in self._securities:
            return self._securities[security]
        security_repo = (
            SecurityRepository(self._connection)
            .filter_by_board(security.board)
            .filter_by_ticker(security.ticker)
        )
        async for record in security_repo:
            self._securities[security] = record.id
            return record.id

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

        repo = CandleRepository(repo=self)
        repo._limit = sl.stop - sl.start
        repo._offset = sl.start
        return repo

    @override
    def filter_by_security(self, security):
        repo = CandleRepository(repo=self)
        repo._filters += [security_table.c["ticker"] == security.ticker]
        repo._filters += [security_table.c["board"] == security.board]
        return repo

    @override
    def filter_by_timeframe(self, timeframe):
        repo = CandleRepository(repo=self)
        repo._filters += [self.table.c["timeframe"] == timeframe.value]
        return repo

    @override
    def filter_by_timestamp_gte(self, timestamp):
        repo = CandleRepository(repo=self)
        repo._filters += [self.table.c["timestamp"] >= timestamp.dt]
        return repo

    @override
    def filter_by_timestamp_lte(self, timestamp):
        repo = CandleRepository(repo=self)
        repo._filters += [self.table.c["timestamp"] <= timestamp.dt]
        return repo
