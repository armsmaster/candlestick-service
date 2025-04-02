from typing import override

from sqlalchemy import Connection, Row, or_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.exc import OperationalError

from app.core.date_time import Timestamp
from app.core.entities import Candle, Security, Timeframe
from app.core.repository import ICandleRepository
from app.exceptions import DatabaseException
from app.repository.sa_repository.base_repo import BaseRepository
from app.repository.sa_repository.metadata import candle_table, security_table


class CandleRepository(BaseRepository, ICandleRepository):

    table = candle_table

    @override
    def __init__(
        self,
        connection: Connection | None = None,
        repo: ICandleRepository | None = None,
    ):
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
    def _row_to_entity(self, row: Row) -> Candle:
        entity = Candle(
            id=row.id,
            security=Security(
                id=row.security_id,
                ticker=row.ticker,
                board=row.board,
            ),
            timeframe=Timeframe(row.timeframe),
            timestamp=Timestamp(row.timestamp),
            open=row.open,
            high=row.high,
            low=row.low,
            close=row.close,
        )
        return entity

    @override
    async def add(self, items: list[Candle]) -> None:
        if len(items) == 0:
            return

        insert_stmt = insert(self.table).on_conflict_do_nothing()
        items_to_insert = [
            {
                "id": item.id,
                "security_id": item.security.id,
                "timeframe": item.timeframe.value,
                "timestamp": item.timestamp.dt,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
            }
            for item in items
        ]
        try:
            await self._connection.execute(insert_stmt, items_to_insert)
        except OperationalError as e:
            raise DatabaseException(f"OperationalError: {str(e)}")

    @override
    async def remove(self, items: list[Candle]):
        statement = self.table.delete().where(
            or_(False, *[self.table.c["id"] == i.id for i in items])
        )
        try:
            await self._connection.execute(statement)
        except OperationalError as e:
            raise DatabaseException(f"OperationalError: {str(e)}")

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
