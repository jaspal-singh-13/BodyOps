"""
Credentials cache backed by the Auth Sheet.

On startup ``load_credentials()`` is called once to populate the module-level
cache with all credential rows.  A background asyncio task (started from
``main.py`` lifespan) calls ``poll_credentials()`` every 60 seconds, compares
the fetched rows to the cached copy, and re-syncs only when something has
actually changed.

All login calls read from ``get_credentials()`` — a pure in-memory lookup
with no I/O.
"""

import asyncio
import os

from ..logger import get_logger
from .sheets_client import get_client
from .sheets_repo import to_int

logger = get_logger("auth_sheet")

_credentials: list[dict] | None = None


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _fetch_from_sheet() -> list[dict]:
    """Fetch all credential rows from the Auth Sheet (synchronous)."""
    sheet_id = os.environ["GOOGLE_AUTH_SHEET_ID"]
    spreadsheet = get_client().open_by_key(sheet_id)
    ws = spreadsheet.sheet1
    rows = ws.get_all_records()
    if not rows:
        raise ValueError("Auth Sheet has no data rows")
    users = []
    for i, row in enumerate(rows):
        if "email" not in row or "password" not in row:
            raise ValueError("Auth Sheet must have 'email' and 'password' columns")
        if not str(row["email"]).strip():
            continue  # skip blank rows
        users.append(
            {
                # Fall back to row position (1-based) so legacy single-row
                # sheets without a user_id column keep user_id=1. A malformed
                # user_id cell also falls back instead of crashing startup.
                "user_id": to_int(row.get("user_id"), i + 1),
                "email": str(row["email"]).strip(),
                "password": str(row["password"]),
            }
        )
    if not users:
        raise ValueError("Auth Sheet has no valid credential rows")
    return users


def _set_credentials(data: list[dict]) -> None:
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
    logger.info("Credentials cache: loaded (%d user(s))", len(data))


def get_credentials() -> list[dict]:
    """
    Return all cached credential rows — pure in-memory lookup, no I/O.

    Raises:
        RuntimeError: If called before ``load_credentials()`` has completed.
    """
    if _credentials is None:
        raise RuntimeError("Credentials not yet loaded — call load_credentials() at startup")
    return _credentials


def find_user(email: str) -> dict | None:
    """
    Return the credential row matching ``email`` (case-insensitive), or None.

    Raises:
        RuntimeError: If called before ``load_credentials()`` has completed.
    """
    for user in get_credentials():
        if user["email"].lower() == email.strip().lower():
            return user
    return None


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
                    "Credentials changed in Auth Sheet — cache re-synced (%d user(s))",
                    len(fresh),
                )
            else:
                logger.debug("Credential poll: no change detected")
        except Exception as exc:
            logger.warning("Credential poll failed (will retry in %ss): %s", interval, exc)
