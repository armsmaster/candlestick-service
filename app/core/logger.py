"""Logger interface."""

from abc import ABC, abstractmethod


class ILogger(ABC):
    """Logger interface."""

    @abstractmethod
    def bind(self, **kwargs):
        """Bind variables."""
        raise NotImplementedError

    @abstractmethod
    def set_level(self, level):
        """Set log level."""
        raise NotImplementedError

    @abstractmethod
    def info(self, *args, **kwargs):
        """Log info."""
        raise NotImplementedError

    @abstractmethod
    def warning(self, *args, **kwargs):
        """Log warning."""
        raise NotImplementedError

    @abstractmethod
    def error(self, *args, **kwargs):
        """Log error."""
        raise NotImplementedError

    @abstractmethod
    def debug(self, *args, **kwargs):
        """Log debug."""
        raise NotImplementedError
