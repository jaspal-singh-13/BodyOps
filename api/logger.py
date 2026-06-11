"""
Centralized logging configuration for the BodyOps backend.

All loggers are namespaced under ``bodyops.*`` so they can be controlled
together via the ``LOG_LEVEL`` env var (default: ``INFO``).

Per-module overrides are supported via ``LOG_LEVEL_<MODULE>`` env vars.
The module suffix maps directly to the ``bodyops.<module>`` logger name.

Examples::

    LOG_LEVEL=INFO            # root bodyops level
    LOG_LEVEL_AGENT=DEBUG     # bodyops.agent and all its children
    LOG_LEVEL_SHEETS=DEBUG    # bodyops.sheets_repo, bodyops.sheets_client

Every log record carries a ``request_id`` field (default ``"-"``) injected
from a ``contextvars.ContextVar`` so that concurrent requests can be
correlated across log lines.

Usage::

    from .logger import get_logger, request_id_var
    logger = get_logger("my_module")
    logger.info("Something happened: %s", value)
"""

import contextvars
import logging
import os

# ---------------------------------------------------------------------------
# Request-correlation context variable
# ---------------------------------------------------------------------------

#: Set this at the start of each HTTP request to correlate all downstream logs.
request_id_var: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="-"
)

# Module-level flag to ensure ``basicConfig`` is only called once per process.
_configured = False


# ---------------------------------------------------------------------------
# Filter that stamps each log record with the current request ID
# ---------------------------------------------------------------------------


class _RequestIdFilter(logging.Filter):
    """Inject the current ``request_id`` into every log record."""

    def filter(self, record: logging.LogRecord) -> bool:  # noqa: A003
        record.request_id = request_id_var.get()  # type: ignore[attr-defined]
        return True


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

#: Third-party namespaces whose verbosity we pin to WARNING to avoid noise.
_QUIET_LOGGERS = [
    "httpx",
    "httpcore",
    "urllib3",
    "google",
    "googleapiclient",
    "openai",
    "hpack",
    "h2",
]

#: Map env-var suffix → bodyops sub-namespace, used for per-module overrides.
#: Add entries here if new sub-packages are introduced.
_MODULE_ENV_MAP: dict[str, str] = {
    "AGENT": "bodyops.agent",
    "SHEETS": "bodyops.sheets",
    "SERVICES": "bodyops.services",
    "ROUTERS": "bodyops.routers",
    "AUTH": "bodyops.auth",
    "MAIN": "bodyops.main",
}


def _configure() -> None:
    """
    Initialize ``logging.basicConfig`` once per process and apply fine-grained
    level overrides from environment variables.

    Root ``bodyops`` level is read from ``LOG_LEVEL`` (default ``INFO``).
    Per-module overrides use ``LOG_LEVEL_<SUFFIX>`` (e.g. ``LOG_LEVEL_AGENT=DEBUG``).
    Third-party noisy loggers are silenced to ``WARNING`` regardless of the
    global level.
    """
    global _configured
    if _configured:
        return

    level_name = os.environ.get("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    fmt = (
        "%(asctime)s [%(levelname)-8s] %(name)s %(funcName)s:%(lineno)d"
        " [req=%(request_id)s] %(message)s"
    )
    logging.basicConfig(level=level, format=fmt)

    # Attach the request-ID filter to the root handler so it runs for all records.
    request_filter = _RequestIdFilter()
    for handler in logging.root.handlers:
        handler.addFilter(request_filter)

    # Set the bodyops root to the requested level explicitly (basicConfig sets
    # the root logger, but we want a dedicated namespace).
    logging.getLogger("bodyops").setLevel(level)

    # Per-module overrides
    for suffix, namespace in _MODULE_ENV_MAP.items():
        override = os.environ.get(f"LOG_LEVEL_{suffix}", "").upper()
        if override:
            override_level = getattr(logging, override, None)
            if override_level is not None:
                logging.getLogger(namespace).setLevel(override_level)

    # Silence noisy third-party libraries so DEBUG output stays readable.
    for name in _QUIET_LOGGERS:
        logging.getLogger(name).setLevel(logging.WARNING)

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
