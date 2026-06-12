"""
Business logic for user settings.

Reads from and writes to the ``Settings`` tab of the Main Data Sheet.
Each user has at most one row, identified by ``user_id``.

Operations are upsert-based: ``save_settings`` checks for an existing row
via ``find_row`` and either updates it or appends a new one.

A 60-second per-user TTL cache avoids redundant full-tab reads when
``get_settings`` is called multiple times per request cycle (e.g. both
``/settings`` and ``/weight/trend`` on the same dashboard load).
``save_settings`` always invalidates the cache for the affected user.
"""

import time
from datetime import datetime, timezone
from typing import Any

import gspread.exceptions

from ..logger import get_logger
from ..models.settings import SettingsCreate, SettingsResponse
from ..sheets.sheets_repo import append_row, find_row, read_rows, to_float, to_int, update_row

logger = get_logger("settings_service")
SETTINGS_TAB = "Settings"

# (cached_at_monotonic, value)
_settings_cache: dict[int, tuple[float, SettingsResponse | None]] = {}
SETTINGS_TTL = 60.0  # seconds


def _cache_get(user_id: int) -> tuple[bool, SettingsResponse | None]:
    """Return (hit, value). hit is True only when the entry is within TTL."""
    entry = _settings_cache.get(user_id)
    if entry is None:
        return False, None
    cached_at, value = entry
    if time.monotonic() - cached_at < SETTINGS_TTL:
        return True, value
    return False, None


def _cache_set(user_id: int, value: SettingsResponse | None) -> None:
    _settings_cache[user_id] = (time.monotonic(), value)


def _cache_invalidate(user_id: int) -> None:
    _settings_cache.pop(user_id, None)


def get_settings(user_id: int) -> SettingsResponse | None:
    """
    Fetch the settings row for a user from the ``Settings`` sheet tab.

    Results are cached for ``SETTINGS_TTL`` seconds (60s) per user to avoid
    redundant full-tab reads across concurrent endpoints on the same page load.

    Args:
        user_id: Authenticated user's integer ID.

    Returns:
        ``SettingsResponse`` populated from the sheet row, or ``None`` if
        no matching row is found.
    """
    hit, cached = _cache_get(user_id)
    if hit:
        logger.debug("Settings cache hit for user_id=%s", user_id)
        return cached

    logger.debug("Fetching settings for user_id=%s", user_id)
    try:
        rows = read_rows(SETTINGS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        logger.warning("Worksheet '%s' not found", SETTINGS_TAB)
        _cache_set(user_id, None)
        return None

    row: dict[str, Any] | None = next(
        (r for r in rows if to_int(r.get("user_id"), -1) == user_id), None
    )
    if row is None:
        logger.debug("No settings row found for user_id=%s", user_id)
        _cache_set(user_id, None)
        return None

    result = SettingsResponse(
        user_id=to_int(row.get("user_id"), 0),
        name=str(row.get("name", "")),
        current_weight_kg=to_float(row.get("current_weight_kg"), 0),
        height_cm=to_float(row.get("height_cm"), 0),
        age=to_int(row.get("age"), 0),
        goal_weight_kg=to_float(row.get("goal_weight_kg"), 0),
        start_date=str(row.get("start_date", "")),
        calorie_target=to_int(row.get("calorie_target"), 0),
        protein_target_g=to_int(row.get("protein_target_g"), 0),
        wake_up_time=str(row.get("wake_up_time", "07:00")),
        unit_preference=str(row.get("unit_preference", "metric")),
        reminders_json=str(row.get("reminders_json", "{}")),
        updated_at=str(row.get("updated_at", "")),
    )
    _cache_set(user_id, result)
    return result


def save_settings(user_id: int, data: SettingsCreate) -> SettingsResponse:
    """
    Upsert the settings row for a user: update if found, append if not.

    Stamps ``updated_at`` with the current UTC ISO timestamp on every save.
    The ``user_id`` in the row always comes from the authenticated caller —
    the ``user_id`` field in ``data`` is ignored in favour of the parameter.

    Invalidates the per-user settings cache so the next ``get_settings`` call
    reads the freshly written row.

    Args:
        user_id: Authenticated user's integer ID (scopes the write).
        data: Full settings payload from the request body.

    Returns:
        ``SettingsResponse`` reflecting the saved state, including ``updated_at``.
    """
    now = datetime.now(timezone.utc).isoformat()
    row_dict = {"user_id": user_id, **data.model_dump(), "updated_at": now}

    try:
        result = find_row(SETTINGS_TAB, "user_id", str(user_id))
    except gspread.exceptions.WorksheetNotFound:
        logger.warning("Worksheet '%s' not found — will append new row", SETTINGS_TAB)
        result = None

    if result is not None:
        row_index, _ = result
        logger.info("Updating settings for user_id=%s (row %s)", user_id, row_index)
        update_row(SETTINGS_TAB, row_index, row_dict)
    else:
        logger.info("Creating settings for user_id=%s", user_id)
        append_row(SETTINGS_TAB, row_dict)

    _cache_invalidate(user_id)
    return SettingsResponse(**row_dict)


def get_reminders(user_id: int) -> dict:
    """
    Return the user's reminder configuration as a parsed dict.

    Reads ``reminders_json`` from the Settings row. Returns an empty dict
    if the field is missing, empty, or unparseable.

    Args:
        user_id: Authenticated user's integer ID.

    Returns:
        Dict parsed from ``reminders_json``, e.g.
        ``{"weigh_in": {"enabled": true, "time": "07:00"}}``.
    """
    import json as _json
    settings = get_settings(user_id)
    if settings is None:
        return {}
    try:
        return _json.loads(settings.reminders_json or "{}")
    except Exception:
        return {}


def save_reminders(user_id: int, reminders: dict) -> dict:
    """
    Persist the user's reminder configuration to the ``reminders_json`` field.

    Reads the existing settings row, updates only ``reminders_json``, and
    writes back via ``update_row``. Does not touch other settings fields.
    Invalidates the settings cache after writing.

    Args:
        user_id: Authenticated user's integer ID.
        reminders: Dict to serialise and store (e.g. reminder toggles + times).

    Returns:
        The saved reminders dict (same as input).

    Raises:
        ValueError: If no settings row exists for the user.
    """
    import json as _json

    try:
        result = find_row(SETTINGS_TAB, "user_id", str(user_id))
    except gspread.exceptions.WorksheetNotFound:
        raise ValueError("Settings not found — complete onboarding first")

    if result is None:
        raise ValueError("Settings not found — complete onboarding first")

    row_index, existing_row = result
    existing_row["reminders_json"] = _json.dumps(reminders)
    existing_row["updated_at"] = datetime.now(timezone.utc).isoformat()
    update_row(SETTINGS_TAB, row_index, existing_row)
    _cache_invalidate(user_id)
    logger.info("Saved reminders for user_id=%s", user_id)
    return reminders
