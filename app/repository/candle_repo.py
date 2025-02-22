from uuid import uuid4
from sqlalchemy import insert, select, delete, and_, or_, join

from app.core.date_time import Timestamp
from app.core.entities import Candle, Security, Timeframe
from app.core.repository import ICandleRepository, CandlePeriod, CandleRepositoryRequest

from app.repository.base_repo import BaseRepository
from app.repository.metadata import candle_table, security_table


class CandleRepository(BaseRepository, ICandleRepository):

    table = candle_table

    async def create(self, items: list[Candle]):
        securities = set([item.security for item in items])
        security_rows = await self._select_raw(
            table=security_table,
            fields=["id", "ticker", "board"],
            filter=self._construct_filter(
                items=securities,
                table=security_table,
                fields={
                    "ticker": "ticker",
                    "board": "board",
                },
            ),
        )
        db_securities = {
            (row["ticker"], row["board"]): row["id"] for row in security_rows
        }
        ands = [
            and_(
                *[
                    self.table.c["security_id"]
                    == db_securities[(i.security.ticker, i.security.board)],
                    self.table.c["timeframe"] == i.timeframe.value,
                    self.table.c["timestamp"] == i.timestamp.dt,
                ]
            )
            for i in items
        ]
        where_clause = or_(*ands)
        j = join(
            candle_table,
            security_table,
            candle_table.c.security_id == security_table.c.id,
        )
        candle_fields = [
            "security_id",
            "timeframe",
            "timestamp",
            "open",
            "high",
            "low",
            "close",
        ]
        security_fields = ["ticker", "board"]
        existing_candles_stmt = (
            select(candle_table.c[*candle_fields], security_table.c[*security_fields])
            .select_from(j)
            .where(where_clause)
        )
        rows = await self.connection.execute(existing_candles_stmt)
        fields_map = {f: i for i, f in enumerate(candle_fields + security_fields)}
        existing_candles = set(
            [
                Candle(
                    security=Security(
                        ticker=row[fields_map["ticker"]], board=row[fields_map["board"]]
                    ),
                    timeframe=Timeframe(row[fields_map["timeframe"]]),
                    timestamp=Timestamp(row[fields_map["timestamp"]]),
                    open=row[fields_map["open"]],
                    high=row[fields_map["high"]],
                    low=row[fields_map["low"]],
                    close=row[fields_map["close"]],
                )
                for row in rows
            ]
        )
        items_to_insert = [item for item in items if item not in existing_candles]
        insert_stmt = insert(self.table)
        items_to_insert = [
            {
                "id": uuid4(),
                "security_id": db_securities[
                    (item.security.ticker, item.security.board)
                ],
                "timeframe": item.timeframe.value,
                "timestamp": item.timestamp.dt,
                "open": item.open,
                "high": item.high,
                "low": item.low,
                "close": item.close,
            }
            for item in items_to_insert
        ]
        if items_to_insert:
            await self.connection.execute(insert_stmt, items_to_insert)
        return

    async def update(self, items: list[Candle]):
        pass

    async def delete(self, items: list[Candle]):
        pass

    async def get_periods(self, security: Security) -> list[CandlePeriod]:
        pass

    async def add_period(self, security: Security, period: CandlePeriod):
        pass

    async def get(self, request: CandleRepositoryRequest) -> list[Candle]:
        pass
