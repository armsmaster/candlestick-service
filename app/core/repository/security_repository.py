from abc import abstractmethod

from app.core.entities import Security
from app.core.repository.base import IRepository


class ISecurityRepository(IRepository):

    @abstractmethod
    def __aiter__(self) -> "ISecurityRepository":
        raise NotImplementedError

    @abstractmethod
    async def __anext__(self) -> Security:
        raise NotImplementedError

    @abstractmethod
    def filter_by_ticker(self, ticker: str) -> "ISecurityRepository":
        raise NotImplementedError

    @abstractmethod
    def filter_by_board(self, board: str) -> "ISecurityRepository":
        raise NotImplementedError
