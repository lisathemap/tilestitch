"""Logging configuration for tilestitch."""

import logging
import sys
from typing import Optional

LOGGER_NAME = "tilestitch"

_LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """Return a child logger under the tilestitch namespace."""
    if name:
        return logging.getLogger(f"{LOGGER_NAME}.{name}")
    return logging.getLogger(LOGGER_NAME)


def configure_logging(
    level: str = "info",
    fmt: Optional[str] = None,
    stream=None,
) -> None:
    """Configure the root tilestitch logger.

    Args:
        level: One of 'debug', 'info', 'warning', 'error', 'critical'.
        fmt: Optional log format string.  Defaults to a sensible preset.
        stream: Output stream.  Defaults to sys.stderr.
    """
    log_level = _LOG_LEVELS.get(level.lower(), logging.INFO)

    if fmt is None:
        fmt = "[%(levelname)s] %(name)s: %(message)s"

    if stream is None:
        stream = sys.stderr

    handler = logging.StreamHandler(stream)
    handler.setFormatter(logging.Formatter(fmt))

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(log_level)

    # Avoid adding duplicate handlers when called multiple times.
    if not logger.handlers:
        logger.addHandler(handler)
    else:
        logger.handlers[0] = handler


def set_level(level: str) -> None:
    """Adjust the log level of the tilestitch logger after initial setup."""
    log_level = _LOG_LEVELS.get(level.lower())
    if log_level is None:
        raise ValueError(
            f"Invalid log level '{level}'. "
            f"Choose from: {', '.join(_LOG_LEVELS)}"
        )
    logging.getLogger(LOGGER_NAME).setLevel(log_level)
