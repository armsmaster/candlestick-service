"""Dependency resolution."""

import logging
from os import environ

from app.core.logger import ILogger
from app.logger.logger import StructLogger


def get_logger() -> ILogger:
    """Get logger."""
    logger = StructLogger()
    log_level = environ.get("LOG_LEVEL")
    match log_level:
        case "DEBUG":
            logger.set_level(logging.DEBUG)
        case "WARNINIG":
            logger.set_level(logging.WARNING)
        case "ERROR":
            logger.set_level(logging.ERROR)
        case "INFO":
            logger.set_level(logging.INFO)
    logger.bind(app="candles-app")
    return logger
