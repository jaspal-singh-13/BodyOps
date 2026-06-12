"""
Business logic for weight tracking.

Reads from and writes to the ``WeightLogs`` tab of the Main Data Sheet.
Each row stores one daily weigh-in scoped by ``user_id``.

Public functions:
    log_weight   — upsert a weigh-in (append or update same-date row).
    get_history  — last 90 days of entries, newest first, with change diffs.
    get_trend    — 7-day moving average + linear-regression goal projection.

Private helpers:
    _compute_moving_avg — rolling 7-day average over all entries.
    _project_goal_date  — OLS regression on last 14 entries → projected date.
"""

from datetime import date as date_type, datetime, timedelta, timezone
from typing import Any

import gspread.exceptions

from ..logger import get_logger
from ..models.weight import WeightEntryCreate, WeightEntryResponse, WeightHistoryItem, WeightTrendResponse
from ..sheets.sheets_repo import append_row, read_rows, update_row

logger = get_logger("weight_service")
WEIGHT_TAB = "WeightLogs"


def _parse_weight(value: Any) -> float | None:
    """Return ``value`` as float, or ``None`` if it cannot be converted.

    Guards against column-mapping drift in the Google Sheet where a ``time``
    string (e.g. ``'04:48'``) occasionally lands in the ``weight_kg`` column.
    """
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def log_weight(user_id: int, data: WeightEntryCreate) -> WeightEntryResponse:
    """
    Upsert a weight entry: append if the date+time is new, update if it exists.

    Scans all rows in ``WeightLogs`` looking for a row where ``user_id``,
    ``date``, and ``time`` all match. If found, updates that row in place.
    Otherwise appends a new row, allowing multiple entries per day.

    ``time`` defaults to the current local HH:MM when not supplied by the caller.
    ``logged_at`` is always set to the current UTC timestamp.

    Args:
        user_id: Authenticated user's integer ID.
        data: ``WeightEntryCreate`` with ``date``, ``weight_kg``, and optional ``time``.

    Returns:
        ``WeightEntryResponse`` reflecting the saved state.
    """
    now = datetime.now(timezone.utc).isoformat()
    entry_time = data.time if data.time else datetime.now().strftime("%H:%M")
    try:
        rows = read_rows(WEIGHT_TAB)
    except gspread.exceptions.WorksheetNotFound:
        rows = []

    existing_index: int | None = None
    for i, row in enumerate(rows):
        if (
            int(row.get("user_id", -1)) == user_id
            and row.get("date") == data.date
            and row.get("time") == entry_time
        ):
            existing_index = i + 2  # +1 for header row, +1 for 0-based → 1-based
            break

    row_dict = {
        "user_id": user_id,
        "date": data.date,
        "time": entry_time,
        "weight_kg": data.weight_kg,
        "logged_at": now,
    }

    if existing_index is not None:
        logger.info("Updating weight entry for user_id=%s date=%s time=%s -> %.2f kg", user_id, data.date, entry_time, data.weight_kg)
        update_row(WEIGHT_TAB, existing_index, row_dict)
    else:
        logger.info("Appending weight entry for user_id=%s date=%s time=%s -> %.2f kg", user_id, data.date, entry_time, data.weight_kg)
        append_row(WEIGHT_TAB, row_dict)

    return WeightEntryResponse(**row_dict)


def get_history(user_id: int) -> list[WeightHistoryItem]:
    """
    Return the last 90 days of weight entries sorted newest first.

    Computes ``change_kg`` as the diff from the chronologically previous entry
    (``None`` for the oldest entry in the window).

    Args:
        user_id: Authenticated user's integer ID.

    Returns:
        List of ``WeightHistoryItem`` objects; empty list if no entries exist
        or if the ``WeightLogs`` tab is missing.
    """
    logger.debug("Fetching weight history for user_id=%s", user_id)
    try:
        rows = read_rows(WEIGHT_TAB)
    except gspread.exceptions.WorksheetNotFound:
        logger.warning("Worksheet '%s' not found — returning empty history", WEIGHT_TAB)
        return []

    # Filter to this user and entries within the 90-day window
    cutoff = (date_type.today() - timedelta(days=90)).isoformat()
    entries: list[dict] = []
    for r in rows:
        if int(r.get("user_id", -1)) != user_id or r.get("date", "") < cutoff:
            continue
        w = _parse_weight(r.get("weight_kg"))
        if w is None:
            logger.warning("Skipping malformed WeightLogs row (weight_kg=%r): %s", r.get("weight_kg"), r)
            continue
        entries.append({
            "date": r["date"],
            "time": r.get("time", ""),
            "weight_kg": w,
            # logged_at is always a correct UTC ISO timestamp — use it as the
            # tiebreaker so entries appear in true insertion order regardless of
            # whether the local `time` field was recorded in the wrong timezone.
            "logged_at": r.get("logged_at", ""),
        })

    # Sort chronologically: primary key is date, tiebreaker is logged_at (UTC).
    # This means an entry logged later always wins even if its local `time` field
    # is smaller (e.g. a chat-logged entry whose time was server-UTC, not local).
    entries.sort(key=lambda e: (e["date"], e["logged_at"]))

    result: list[WeightHistoryItem] = []
    for i, entry in enumerate(entries):
        prev = entries[i - 1]["weight_kg"] if i > 0 else None
        change = round(entry["weight_kg"] - prev, 2) if prev is not None else None
        result.append(WeightHistoryItem(date=entry["date"], time=entry["time"], weight_kg=entry["weight_kg"], change_kg=change))

    result.reverse()
    return result


def get_trend(user_id: int, goal_weight_kg: float) -> WeightTrendResponse:
    """
    Compute the 7-day moving average and a linear-regression goal projection.

    Uses all historical entries (not just 90 days) for the moving average.
    The projection uses the last 14 entries via OLS regression.

    Args:
        user_id: Authenticated user's integer ID.
        goal_weight_kg: Target body weight used for the projection calculation.

    Returns:
        ``WeightTrendResponse`` with ``moving_avg``, ``total_loss_kg``, and
        ``projected_goal_date``. All fields are ``None``/empty when fewer than
        2 entries exist.
    """
    logger.debug("Computing trend for user_id=%s goal=%.2f kg", user_id, goal_weight_kg)
    try:
        rows = read_rows(WEIGHT_TAB)
    except gspread.exceptions.WorksheetNotFound:
        logger.warning("Worksheet '%s' not found — returning empty trend", WEIGHT_TAB)
        return WeightTrendResponse(moving_avg=[], total_loss_kg=None, projected_goal_date=None)

    raw: list[dict] = []
    for r in rows:
        if int(r.get("user_id", -1)) != user_id:
            continue
        w = _parse_weight(r.get("weight_kg"))
        if w is None:
            logger.warning("Skipping malformed WeightLogs row (weight_kg=%r): %s", r.get("weight_kg"), r)
            continue
        raw.append({"date": r["date"], "time": r.get("time", ""), "weight_kg": w})
    all_entries = sorted(raw, key=lambda e: (e["date"], e["time"]))
    # Use the last entry per day so multiple daily logs don't skew the trend chart
    seen: dict[str, dict] = {}
    for e in all_entries:
        seen[e["date"]] = e
    entries = list(seen.values())

    if not entries:
        return WeightTrendResponse(moving_avg=[], total_loss_kg=None, projected_goal_date=None)

    moving_avg = _compute_moving_avg(entries)

    # Total loss: first entry minus last entry (positive = lost weight)
    total_loss = None
    if len(entries) >= 2:
        total_loss = round(entries[0]["weight_kg"] - entries[-1]["weight_kg"], 2)

    projected = _project_goal_date(entries, goal_weight_kg)

    return WeightTrendResponse(
        moving_avg=moving_avg,
        total_loss_kg=total_loss,
        projected_goal_date=projected,
    )


def _compute_moving_avg(entries: list[dict], window: int = 7) -> list[dict]:
    """
    Compute a rolling moving average over a list of dated weight entries.

    The first ``window - 1`` entries will have ``ma_7 = None`` because there
    are not yet enough data points to fill the window.

    Args:
        entries: Chronologically sorted list of ``{date, weight_kg}`` dicts.
        window: Number of entries in the rolling window. Defaults to 7.

    Returns:
        List of ``{date, weight_kg, ma_7}`` dicts in the same order as input.
        ``ma_7`` is ``None`` for entries with fewer than ``window`` predecessors.
    """
    result = []
    for i, entry in enumerate(entries):
        if i >= window - 1:
            window_weights = [entries[j]["weight_kg"] for j in range(i - window + 1, i + 1)]
            ma: float | None = round(sum(window_weights) / window, 2)
        else:
            ma = None
        result.append({"date": entry["date"], "weight_kg": entry["weight_kg"], "ma_7": ma})
    return result


def _project_goal_date(entries: list[dict], goal_weight_kg: float) -> str | None:
    """
    Project the date when the user will reach ``goal_weight_kg`` via OLS regression.

    Uses the last 14 entries (or all entries if fewer than 14). If the trend
    is flat or upward (slope ≥ 0), or the projection is more than 5 years away,
    returns ``None``.

    Args:
        entries: Chronologically sorted list of ``{date, weight_kg}`` dicts.
            Should contain at least 2 entries.
        goal_weight_kg: Target weight in kilograms.

    Returns:
        ISO ``YYYY-MM-DD`` string of the projected goal date, or ``None``
        if the projection is unavailable.
    """
    # Use at most the last 14 entries for a stable short-term regression
    subset = entries[-14:]
    n = len(subset)
    if n < 2:
        return None

    # Convert dates to integer day offsets from the first entry in the subset
    base = date_type.fromisoformat(subset[0]["date"])
    xs = [(date_type.fromisoformat(e["date"]) - base).days for e in subset]
    ys = [e["weight_kg"] for e in subset]

    # Ordinary least squares: y = mx + b
    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xx = sum(x * x for x in xs)
    sum_xy = sum(x * y for x, y in zip(xs, ys))

    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        return None  # All entries on the same date — degenerate case

    m = (n * sum_xy - sum_x * sum_y) / denom
    b = (sum_y - m * sum_x) / n

    if m >= 0:
        return None  # Flat or upward trend — goal unreachable at current pace

    # Solve for x when y = goal_weight_kg: x = (goal - b) / m
    x_goal = (goal_weight_kg - b) / m
    projected = base + timedelta(days=round(x_goal))

    # Sanity check: reject projections more than 5 years away
    today = date_type.today()
    if (projected - today).days > 5 * 365:
        return None

    return projected.isoformat()
