from os import path
import json
from typing import override

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

    def _row_to_record(self, row: dict) -> Record:
        pass

    def _sort(self) -> None:
        for field in reversed(self._order_by):
            self._rows.sort(key=lambda x: x[field])

    def _dump_rows(self, filename: str) -> None:
        dir = path.dirname(__file__)
        json.dump(
            self._rows,
            open(path.join(dir, filename), "w"),
            indent=2,
            sort_keys=True,
        )

    def _load_rows(self, filename: str) -> None:
        dir = path.dirname(__file__)
        try:
            self._rows = json.load(open(path.join(dir, filename), "r"))
        except Exception as e:
            self._rows = list()
