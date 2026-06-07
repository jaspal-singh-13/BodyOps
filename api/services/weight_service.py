"""Business logic for weight tracking."""
from datetime import date as date_type, datetime, timedelta, timezone

import gspread.exceptions

from ..logger import get_logger
from ..models.weight import WeightEntryCreate, WeightEntryResponse, WeightHistoryItem, WeightTrendResponse
from ..sheets.sheets_repo import append_row, read_rows, update_row

logger = get_logger("weight_service")
WEIGHT_TAB = "WeightLogs"


def log_weight(user_id: int, data: WeightEntryCreate) -> WeightEntryResponse:
    """Upsert: append if date not yet logged for this user, update if it is."""
    now = datetime.now(timezone.utc).isoformat()
    try:
        rows = read_rows(WEIGHT_TAB)
    except gspread.exceptions.WorksheetNotFound:
        rows = []

    existing_index: int | None = None
    for i, row in enumerate(rows):
        if int(row.get("user_id", -1)) == user_id and row.get("date") == data.date:
            existing_index = i + 2  # +1 for header row, +1 for 0→1-based
            break

    row_dict = {
        "user_id": user_id,
        "date": data.date,
        "weight_kg": data.weight_kg,
        "logged_at": now,
    }

    if existing_index is not None:
        logger.info("Updating weight entry for user_id=%s date=%s -> %.2f kg", user_id, data.date, data.weight_kg)
        update_row(WEIGHT_TAB, existing_index, row_dict)
    else:
        logger.info("Appending weight entry for user_id=%s date=%s -> %.2f kg", user_id, data.date, data.weight_kg)
        append_row(WEIGHT_TAB, row_dict)

    return WeightEntryResponse(**row_dict)


def get_history(user_id: int) -> list[WeightHistoryItem]:
    """Return last 90 days of entries sorted newest first with change diffs."""
    logger.debug("Fetching weight history for user_id=%s", user_id)
    try:
        rows = read_rows(WEIGHT_TAB)
    except gspread.exceptions.WorksheetNotFound:
        logger.warning("Worksheet '%s' not found — returning empty history", WEIGHT_TAB)
        return []

    cutoff = (date_type.today() - timedelta(days=90)).isoformat()

    entries = [
        {"date": r["date"], "weight_kg": float(r["weight_kg"])}
        for r in rows
        if int(r.get("user_id", -1)) == user_id and r.get("date", "") >= cutoff
    ]

    entries.sort(key=lambda e: e["date"])

    result: list[WeightHistoryItem] = []
    for i, entry in enumerate(entries):
        prev = entries[i - 1]["weight_kg"] if i > 0 else None
        change = round(entry["weight_kg"] - prev, 2) if prev is not None else None
        result.append(WeightHistoryItem(date=entry["date"], weight_kg=entry["weight_kg"], change_kg=change))

    result.reverse()
    return result


def get_trend(user_id: int, goal_weight_kg: float) -> WeightTrendResponse:
    """Compute 7-day moving average and linear-regression projected goal date."""
    logger.debug("Computing trend for user_id=%s goal=%.2f kg", user_id, goal_weight_kg)
    try:
        rows = read_rows(WEIGHT_TAB)
    except gspread.exceptions.WorksheetNotFound:
        logger.warning("Worksheet '%s' not found — returning empty trend", WEIGHT_TAB)
        return WeightTrendResponse(moving_avg=[], total_loss_kg=None, projected_goal_date=None)

    entries = sorted(
        [
            {"date": r["date"], "weight_kg": float(r["weight_kg"])}
            for r in rows
            if int(r.get("user_id", -1)) == user_id
        ],
        key=lambda e: e["date"],
    )

    if not entries:
        return WeightTrendResponse(moving_avg=[], total_loss_kg=None, projected_goal_date=None)

    moving_avg = _compute_moving_avg(entries)

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
    subset = entries[-14:]
    n = len(subset)
    if n < 2:
        return None

    base = date_type.fromisoformat(subset[0]["date"])
    xs = [(date_type.fromisoformat(e["date"]) - base).days for e in subset]
    ys = [e["weight_kg"] for e in subset]

    sum_x = sum(xs)
    sum_y = sum(ys)
    sum_xx = sum(x * x for x in xs)
    sum_xy = sum(x * y for x, y in zip(xs, ys))

    denom = n * sum_xx - sum_x * sum_x
    if denom == 0:
        return None

    m = (n * sum_xy - sum_x * sum_y) / denom
    b = (sum_y - m * sum_x) / n

    if m >= 0:
        return None

    x_goal = (goal_weight_kg - b) / m
    projected = base + timedelta(days=round(x_goal))

    today = date_type.today()
    if (projected - today).days > 5 * 365:
        return None

    return projected.isoformat()
