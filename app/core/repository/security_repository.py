from abc import ABC, abstractmethod

from app.core.entities import Security
from app.core.repository.base import IRepository, Record


class ISecurityRepository(IRepository, ABC):

    @abstractmethod
    def __aiter__(self) -> "ISecurityRepository":
        raise NotImplementedError

    @abstractmethod
    async def __anext__(self) -> Record[Security]:
        raise NotImplementedError

    @abstractmethod
    def filter_by_ticker(self, ticker: str) -> "ISecurityRepository":
        raise NotImplementedError

    @abstractmethod
    def filter_by_board(self, board: str) -> "ISecurityRepository":
        raise NotImplementedError
