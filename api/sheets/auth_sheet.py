"""
Credentials cache backed by the Auth Sheet.

On startup ``load_credentials()`` is called once to populate the module-level
cache.  A background asyncio task (started from ``main.py`` lifespan) calls
``poll_credentials()`` every 60 seconds, compares the fetched row to the
cached copy, and re-syncs only when something has actually changed.

All login calls read from ``get_credentials()`` — a pure in-memory lookup
with no I/O.
"""

import asyncio
import os

from ..logger import get_logger
from .sheets_client import get_client

logger = get_logger("auth_sheet")

_credentials: dict | None = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _fetch_from_sheet() -> dict:
    """Fetch the first credential row from the Auth Sheet (synchronous)."""
    sheet_id = os.environ["GOOGLE_AUTH_SHEET_ID"]
    spreadsheet = get_client().open_by_key(sheet_id)
    ws = spreadsheet.sheet1
    rows = ws.get_all_records()
    if not rows:
        raise ValueError("Auth Sheet has no data rows")
    row = rows[0]
    if "email" not in row or "password" not in row:
        raise ValueError("Auth Sheet must have 'email' and 'password' columns")
    return {
        "user_id": int(row["user_id"]) if row.get("user_id") else 1,
        "email": str(row["email"]),
        "password": str(row["password"]),
    }


def _set_credentials(data: dict) -> None:
    global _credentials
    _credentials = data


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def load_credentials() -> None:
    """
    Fetch credentials from the Auth Sheet and populate the in-memory cache.

    Called once during the FastAPI lifespan startup (via asyncio.to_thread).
    """
    data = _fetch_from_sheet()
    _set_credentials(data)
    logger.info("Credentials cache: loaded (user_id=%s)", data.get("user_id"))


def get_credentials() -> dict:
    """
    Return cached credentials — pure in-memory lookup, no I/O.

    Raises:
        RuntimeError: If called before ``load_credentials()`` has completed.
    """
    if _credentials is None:
        raise RuntimeError("Credentials not yet loaded — call load_credentials() at startup")
    return _credentials


async def poll_credentials(interval: int = 60) -> None:
    """
    Background asyncio task: re-sync credentials whenever the Auth Sheet changes.

    Runs forever (until the process shuts down).  Sleeps for ``interval``
    seconds between checks.  Only updates the cache when the fetched row
    differs from the current cached copy, so quiet periods produce no churn.

    Args:
        interval: Seconds between polls. Defaults to 60.
    """
    while True:
        await asyncio.sleep(interval)
        try:
            fresh = await asyncio.to_thread(_fetch_from_sheet)
            if fresh != _credentials:
                _set_credentials(fresh)
                logger.warning(
                    "Credentials changed in Auth Sheet — cache re-synced (user_id=%s)",
                    fresh.get("user_id"),
                )
            else:
                logger.debug("Credential poll: no change detected")
        except Exception as exc:
            logger.warning("Credential poll failed (will retry in %ss): %s", interval, exc)
