from dataclasses import dataclass
from typing import Any, override

from sqlalchemy import Connection
from sqlalchemy import Table, or_, and_, select, func

from sqlalchemy import ColumnExpressionArgument, ColumnElement, Select
from sqlalchemy import Row

from app.core.entities import Entity
from app.core.repository.base import IRepository
from app.core.repository.base import Record


class BaseRepository(IRepository):

    def __init__(
        self,
        order_by: list[str] = [],
    ):
        self._order_by: list[str] = order_by
        self._rows: list[dict] = None

    @override
    async def count(self) -> int:
        out = len(self._rows)
        return out

    @override
    def __aiter__(self) -> "IRepository":
        self.index = 0
        return self

    @override
    async def __anext__(self) -> Record:

        if self.index < len(self._rows):
            row: dict = self._rows[self.index]
            record = self._row_to_record(row)
            self.index += 1
            return record
        raise StopAsyncIteration

    def _row_to_record(self, row: Row) -> Record:
        pass
