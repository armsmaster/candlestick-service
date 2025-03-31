from uuid import UUID

from pydantic import BaseModel


class SecuritySchema(BaseModel):
    id: UUID
    ticker: str
    board: str
