from sqlalchemy import Connection

from app.core.repository import IRepository


class BaseRepository(IRepository):

    def __init__(self, connection: Connection):
        self.connection = connection
