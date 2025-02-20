from os import environ
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from pytest import fixture
from dotenv import load_dotenv

from app.core.entities import Security
from app.repository.security_repo import SecurityRepository

load_dotenv()


class UOW:

    def __init__(self, session: Session):
        self.session = session

    def __enter__(self):
        pass

    def __exit__(self, exc_type, exc_val, traceback) -> bool:
        self.session.commit()


@fixture
def db_session():
    url = "{drivername}://{username}:{password}@{host}:{port}/{database}".format(
        drivername=environ.get("DB_DRIVER"),
        username=environ.get("POSTGRES_USER"),
        password=environ.get("POSTGRES_PASSWORD"),
        host=environ.get("PG_HOST"),
        port=environ.get("PG_PORT"),
        database=environ.get("POSTGRES_DB"),
    )
    engine = create_engine(url)
    Session = sessionmaker(engine, autoflush=False)

    with Session() as session:
        yield session


def test_security_repository(db_session):
    security = Security(ticker="AAA", board="BBB")

    with UOW(db_session):
        repo = SecurityRepository(session=db_session)
        repo.create([security])

    with UOW(db_session):
        repo = SecurityRepository(session=db_session)
        assert security in repo.all()

    with UOW(db_session):
        repo = SecurityRepository(session=db_session)
        repo.delete([security])

    with UOW(db_session):
        repo = SecurityRepository(session=db_session)
        assert security not in repo.all()
