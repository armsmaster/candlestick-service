from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, UUID, Float, DateTime

metadata_obj = MetaData()

security_table = Table(
    "security",
    metadata_obj,
    Column("id", UUID, primary_key=True),
    Column("ticker", String),
    Column("board", String),
)

candle_table = Table(
    "candle",
    metadata_obj,
    Column("id", UUID, primary_key=True),
    Column("security_id", UUID),
    Column("timeframe", String),
    Column("timestamp", DateTime),
    Column("open", Float),
    Column("high", Float),
    Column("low", Float),
    Column("close", Float),
)
