"""Logger implementation."""

import structlog

from app.core.logger import ILogger


class StructLogger(ILogger):
    """Logger."""

    def __init__(self):
        """Initialize."""
        self._logger: structlog.stdlib.BoundLogger = structlog.get_logger()

    def bind(self, **kwargs):
        """Bind variables."""
        self._logger = self._logger.bind(**kwargs)

    def set_level(self, level):
        """Set log level."""
        self._logger.setLevel(level)

    def info(self, *args, **kwargs):
        """Log info."""
        self._logger.info(*args, **kwargs)

    def warning(self, *args, **kwargs):
        """Log warning."""
        self._logger.warning(*args, **kwargs)

    def error(self, *args, **kwargs):
        """Log error."""
        self._logger.error(*args, **kwargs)

    def debug(self, *args, **kwargs):
        """Log debug."""
        self._logger.debug(*args, **kwargs)
