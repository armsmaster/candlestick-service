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

from app.repository.base_repo import BaseRepository
from app.repository.security_repo import SecurityRepository
from app.repository.metadata import security_table, candle_span_table


class CandleSpanRepository(BaseRepository, ICandleSpanRepository):

    table = candle_span_table

    @override
    def __init__(
        self,
        connection: Connection | None = None,
        repo: ICandleSpanRepository | None = None,
    ):
        self._securities: dict[Security, UUID] = {}
        super().__init__(
            connection=connection if repo is None else repo._connection,
            table=self.table,
            filters=[] if repo is None else list(repo._filters),
            order_by=["date_from"] if repo is None else list(repo._order_by),
        )

    @override
    def _construct_select_base(self):
        return select(candle_span_table, security_table).join(
            security_table,
            security_table.c["id"] == candle_span_table.c["security_id"],
        )

    @override
    def _row_to_record(self, row: Row) -> Record:
        record = Record(
            id=row.id,
            entity=CandleSpan(
                security=Security(
                    ticker=row.ticker,
                    board=row.board,
                ),
                timeframe=Timeframe(row.timeframe),
                date_from=Timestamp(row.date_from),
                date_till=Timestamp(row.date_till),
            ),
        )
        return record

    @override
    async def add(self, items: list[CandleSpan]) -> None:
        if len(items) == 0:
            return

        insert_stmt = insert(self.table).on_conflict_do_nothing()
        items_to_insert = [
            {
                "id": uuid4(),
                "security_id": await self._get_security_id(item.security),
                "timeframe": item.timeframe.value,
                "date_from": item.date_from.dt,
                "date_till": item.date_till.dt,
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

        repo = CandleSpanRepository(repo=self)
        repo._limit = sl.stop - sl.start
        repo._offset = sl.start
        return repo

    @override
    def filter_by_security(self, security):
        repo = CandleSpanRepository(repo=self)
        repo._filters += [security_table.c["ticker"] == security.ticker]
        repo._filters += [security_table.c["board"] == security.board]
        return repo

    @override
    def filter_by_timeframe(self, timeframe):
        repo = CandleSpanRepository(repo=self)
        repo._filters += [self.table.c["timeframe"] == timeframe.value]
        return repo
