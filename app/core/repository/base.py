from abc import ABC, abstractmethod

from app.core.entities import Entity


class IRepository(ABC):

    @abstractmethod
    async def count(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def __aiter__(self) -> "IRepository":
        raise NotImplementedError

    @abstractmethod
    async def __anext__(self) -> Entity:
        raise NotImplementedError

    @abstractmethod
    def __getitem__(self, s: slice) -> "IRepository":
        raise NotImplementedError

    @abstractmethod
    async def add(self, items: list[Entity]) -> None:
        pass

    @abstractmethod
    async def remove(self, items: list[Entity]) -> None:
        pass
