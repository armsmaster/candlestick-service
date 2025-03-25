"""Base classes for Use Case component."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass
class UseCaseEvent:
    """Base UseCase Event."""

    pass


@dataclass
class UseCaseRequest:
    """Base UseCase Request."""

    pass


@dataclass
class UseCaseResponse:
    """Base UseCase Response."""

    result: Any | None = None
    errors: list[str] = field(default_factory=list)


class BaseUseCase(ABC):
    """Base class for use cases."""

    @abstractmethod
    async def execute(self, request: UseCaseRequest) -> UseCaseResponse:
        """Execute use case."""
        raise NotImplementedError

    async def log_event(self, event: UseCaseEvent) -> None:
        """Log use case event."""
        pass
