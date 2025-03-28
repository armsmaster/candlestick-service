"""Dependency resolution."""

from app.core.logger import ILogger
from app.logger.logger import StructLogger


def get_logger() -> ILogger:
    """Get logger."""
    logger = StructLogger()
    logger.bind(app="candles-app")
    return logger
