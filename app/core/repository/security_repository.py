from abc import ABC, abstractmethod


from app.core.repository.base import IRepository


class ISecurityRepository(IRepository, ABC):

    @abstractmethod
    def filter_by_ticker(self, ticker: str) -> "ISecurityRepository":
        raise NotImplementedError

    @abstractmethod
    def filter_by_board(self, board: str) -> "ISecurityRepository":
        raise NotImplementedError
