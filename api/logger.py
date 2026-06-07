"""Centralized logging configuration for the BodyOps backend."""
import logging
import os

_configured = False


def _configure() -> None:
    global _configured
    if _configured:
        return

    level = os.environ.get("LOG_LEVEL", "INFO").upper()
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    logging.basicConfig(level=getattr(logging, level, logging.INFO), format=fmt)
    _configured = True


def get_logger(name: str) -> logging.Logger:
    _configure()
    return logging.getLogger(f"bodyops.{name}")
