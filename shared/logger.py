from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Final

from loguru import logger as _logger


DEFAULT_LOG_LEVEL: Final[str] = "INFO"
DEFAULT_LOG_DIR: Final[str] = "logs"
DEFAULT_LOG_FILE: Final[str] = "atos.log"

VALID_LOG_LEVELS: Final[set[str]] = {
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
}


def _resolve_log_level() -> str:
    """
    Resolve the active log level from environment variables.

    Invalid values safely fall back to INFO instead of crashing the platform
    during startup.
    """
    configured_level = os.getenv("ATOS_LOG_LEVEL", DEFAULT_LOG_LEVEL).strip().upper()

    if configured_level not in VALID_LOG_LEVELS:
        return DEFAULT_LOG_LEVEL

    return configured_level


def _resolve_log_dir() -> Path:
    """
    Resolve the log directory.

    The default is the local runtime logs directory. This can be overridden
    using ATOS_LOG_DIR in deployment environments.
    """
    configured_dir = os.getenv("ATOS_LOG_DIR", DEFAULT_LOG_DIR).strip()

    if not configured_dir:
        configured_dir = DEFAULT_LOG_DIR

    return Path(configured_dir)


def _resolve_log_file() -> str:
    """
    Resolve the log file name.

    The default is atos.log. This can be overridden using ATOS_LOG_FILE.
    """
    configured_file = os.getenv("ATOS_LOG_FILE", DEFAULT_LOG_FILE).strip()

    if not configured_file:
        return DEFAULT_LOG_FILE

    return configured_file


def configure_logging() -> None:
    """
    Configure the global ATOS logger.

    This setup:
    - Removes Loguru's default handler.
    - Adds a structured console handler.
    - Adds a rotating file handler.
    - Prevents duplicated log handlers.
    - Keeps sensitive diagnostics disabled by default.
    """
    log_level = _resolve_log_level()
    log_dir = _resolve_log_dir()
    log_file = _resolve_log_file()

    log_dir.mkdir(parents=True, exist_ok=True)

    _logger.remove()

    _logger.add(
        sys.stderr,
        level=log_level,
        format=(
            "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        ),
        enqueue=True,
        backtrace=False,
        diagnose=False,
    )

    _logger.add(
        log_dir / log_file,
        level=log_level,
        rotation="10 MB",
        retention="14 days",
        compression="zip",
        enqueue=True,
        backtrace=False,
        diagnose=False,
        encoding="utf-8",
    )


configure_logging()

logger = _logger

__all__ = ["logger", "configure_logging"]