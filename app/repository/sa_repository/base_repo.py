from dataclasses import dataclass
from typing import Any, override

from sqlalchemy import (
    ColumnElement,
    ColumnExpressionArgument,
    Connection,
    Row,
    Select,
    Table,
    and_,
    func,
    select,
)
from sqlalchemy.exc import OperationalError

from app.core.entities import Entity
from app.core.repository import IRepository
from app.exceptions import DatabaseException


@dataclass
class Filter:
    field: str
    value: Any


@dataclass
class FilterGroup:
    filters: list[Filter]


class BaseRepository(IRepository):

    def __init__(
        self,
        connection: Connection,
        table: Table,
        filters: list[ColumnExpressionArgument] = [],
        order_by: list[str] = [],
    ):
        self._connection = connection
        self._table = table
        self._filters: list[ColumnExpressionArgument] = filters
        self._order_by: list[str] = order_by
        self._limit: int | None = None
        self._offset: int | None = None
        self._rows = None

    def _construct_select_base(self) -> Select:
        return select(self._table)

    def _construct_select(self) -> Select:
        statement = (
            self._construct_select_base()
            .where(self._construct_where())
            .order_by(*self._order_by)
            .offset(self._offset)
            .limit(self._limit)
        )
        return statement

    def _construct_count(self) -> Select:
        sub_query = (
            self._construct_select_base()
            .where(self._construct_where())
            .order_by(*self._order_by)
            .offset(self._offset)
            .limit(self._limit)
            .subquery()
        )
        statement = select(func.count("*")).select_from(sub_query)
        return statement

    def _construct_where(self) -> ColumnElement:
        where = and_(1 == 1, *self._filters)
        return where

    @override
    async def count(self) -> int:
        statement = self._construct_count()
        try:
            result = await self._connection.execute(statement)
        except OperationalError as e:
            raise DatabaseException(f"OperationalError: {str(e)}")
        out = result.scalar_one()
        return out

    @override
    def __aiter__(self) -> "IRepository":
        self.index = 0
        return self

    @override
    async def __anext__(self) -> Entity:
        if self._rows is None:
            statement = self._construct_select()

            try:
                self._rows = await self._connection.execute(statement)
            except OperationalError as e:
                raise DatabaseException(f"OperationalError: {str(e)}")

            self._rows: list[Row] = list(self._rows)

        if self.index < len(self._rows):
            row: Row = self._rows[self.index]
            record = self._row_to_entity(row)
            self.index += 1
            return record
        raise StopAsyncIteration

    def _row_to_entity(self, row: Row) -> Entity:
        pass

    async def _select_raw(
        self,
        table: Table,
        fields: list[str],
        filter=None,
    ) -> list[dict]:
        where_clause = filter if filter is not None else 1 == 1
        existing_stmt = select(table.c[*fields]).where(where_clause)
        rows = await self._connection.execute(existing_stmt)
        return [{field: row[i] for i, field in enumerate(fields)} for row in rows]
