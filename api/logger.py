"""
Centralized logging configuration for the BodyOps backend.

All loggers are namespaced under ``bodyops.*`` so they can be controlled
together via ``LOG_LEVEL`` env var (default: ``INFO``).

Usage::

    from .logger import get_logger
    logger = get_logger("my_module")
    logger.info("Something happened: %s", value)
"""

import logging
import os

# Module-level flag to ensure ``basicConfig`` is only called once per process.
_configured = False


def _configure() -> None:
    """
    Initialize ``logging.basicConfig`` once per process.

    Level is read from ``LOG_LEVEL`` env var (e.g. ``DEBUG``, ``INFO``,
    ``WARNING``). Defaults to ``INFO`` if the var is missing or invalid.
    """
    global _configured
    if _configured:
        return

    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format=fmt)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    """
    Return a namespaced logger, configuring the root handler on first call.

    Args:
        name: Short module name (e.g. ``"auth"``, ``"weight_service"``).
              Will be prefixed with ``"bodyops."`` in log output.

    Returns:
        A ``logging.Logger`` instance named ``bodyops.<name>``.
    """
    _configure()
    return logging.getLogger(f"bodyops.{name}")
