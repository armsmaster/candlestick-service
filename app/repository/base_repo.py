from sqlalchemy import Connection
from sqlalchemy import Table, or_, and_, select

from app.core.entities import Object
from app.core.repository import IRepository


class BaseRepository(IRepository):

    def __init__(self, connection: Connection):
        self.connection = connection

    def _construct_filter(
        self,
        items: list[Object],
        table: Table,
        fields: dict[str, str],
    ):
        cols = table.c
        ands = [
            and_(
                *[
                    cols[db_field] == item.__dict__[entity_field]
                    for entity_field, db_field in fields.items()
                ]
            )
            for item in items
        ]
        return or_(*ands)

    async def _select_raw(
        self,
        table: Table,
        fields: list[str],
        filter=None,
    ) -> list[dict]:
        where_clause = filter if filter is not None else 1 == 1
        existing_stmt = select(table.c[*fields]).where(where_clause)
        rows = await self.connection.execute(existing_stmt)
        return [{field: row[i] for i, field in enumerate(fields)} for row in rows]
