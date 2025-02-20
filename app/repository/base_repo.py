from sqlalchemy import Engine
from sqlalchemy.orm import Session

from app.core.entities import Object
from app.core.repository import IRepository


class BaseRepository(IRepository):

    def __init__(self, session: Session):
        self.session = session
