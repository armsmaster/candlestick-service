from os import environ
from sqlalchemy import create_engine, Connection
from pytest import fixture
from dotenv import load_dotenv

from app.core.entities import Security
from app.repository.security_repo import SecurityRepository

load_dotenv()


class UOW:

    def __init__(self, connection: Connection):
        self.connection = connection

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, traceback) -> bool:
        self.connection.commit()


@fixture
def connection():
    url = "{drivername}://{username}:{password}@{host}:{port}/{database}".format(
        drivername=environ.get("DB_DRIVER"),
        username=environ.get("POSTGRES_USER"),
        password=environ.get("POSTGRES_PASSWORD"),
        host=environ.get("PG_HOST"),
        port=environ.get("PG_PORT"),
        database=environ.get("POSTGRES_DB"),
    )
    engine = create_engine(url)

    with engine.connect() as connection:
        yield connection


def test_security_repository(connection: Connection):
    security = Security(ticker="AAA", board="BBB")

    with UOW(connection):
        repo = SecurityRepository(connection=connection)
        repo.create([security])

    with UOW(connection):
        repo = SecurityRepository(connection=connection)
        assert security in repo.all()

    with UOW(connection):
        repo = SecurityRepository(connection=connection)
        repo.delete([security])

    with UOW(connection):
        repo = SecurityRepository(connection=connection)
        assert security not in repo.all()
