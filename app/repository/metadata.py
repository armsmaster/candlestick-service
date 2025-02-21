from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, UUID

metadata_obj = MetaData()

security_table = Table(
    "security",
    metadata_obj,
    Column("id", UUID, primary_key=True),
    Column("ticker", String),
    Column("board", String),
)
