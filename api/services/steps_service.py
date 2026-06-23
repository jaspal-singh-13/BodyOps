from datetime import date as date_type, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import gspread.exceptions

from ..logger import get_logger
from ..models.steps import StepsEntryCreate, StepsEntryResponse, StepsHistoryItem
from ..sheets.sheets_repo import append_row, delete_row, read_rows, to_int, update_row

logger = get_logger("steps_service")
STEPS_TAB = "StepsLogs"


def log_steps(user_id: int, data: StepsEntryCreate, tz_str: str = "UTC") -> StepsEntryResponse:
    now = datetime.now(timezone.utc).isoformat()
    try:
        _tz = ZoneInfo(tz_str)
    except Exception:
        _tz = timezone.utc
    entry_time = data.time if data.time else datetime.now(_tz).strftime("%H:%M")

    try:
        rows = read_rows(STEPS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        rows = []

    # Upsert by (user_id, date) — one steps entry per day
    existing_index: int | None = None
    for i, row in enumerate(rows):
        if to_int(row.get("user_id"), -1) == user_id and row.get("date") == data.date:
            existing_index = i + 2  # +1 header, +1 0-based → 1-based
            break

    row_dict = {
        "user_id": user_id,
        "date": data.date,
        "time": entry_time,
        "steps": data.steps,
        "logged_at": now,
    }

    if existing_index is not None:
        logger.info("Updating steps for user_id=%s date=%s -> %d", user_id, data.date, data.steps)
        update_row(STEPS_TAB, existing_index, row_dict)
    else:
        logger.info("Appending steps for user_id=%s date=%s -> %d", user_id, data.date, data.steps)
        append_row(STEPS_TAB, row_dict)

    return StepsEntryResponse(**row_dict)


def delete_steps(user_id: int, date: str, time_str: str) -> None:
    try:
        rows = read_rows(STEPS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        raise ValueError(f"No steps entry found for date={date}")

    for i, row in enumerate(rows):
        if to_int(row.get("user_id"), -1) == user_id and row.get("date") == date:
            row_index = i + 2
            logger.info("Deleting steps entry user_id=%s date=%s", user_id, date)
            delete_row(STEPS_TAB, row_index)
            return

    raise ValueError(f"No steps entry found for date={date}")


def get_history(user_id: int) -> list[StepsHistoryItem]:
    try:
        rows = read_rows(STEPS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return []

    cutoff = (date_type.today() - timedelta(days=90)).isoformat()
    entries: list[dict] = []
    for r in rows:
        if to_int(r.get("user_id"), -1) != user_id or r.get("date", "") < cutoff:
            continue
        try:
            steps = int(r.get("steps", 0))
        except (ValueError, TypeError):
            continue
        entries.append({
            "date": r["date"],
            "time": r.get("time", ""),
            "steps": steps,
            "logged_at": r.get("logged_at", ""),
        })

    entries.sort(key=lambda e: (e["date"], e["logged_at"]))

    result: list[StepsHistoryItem] = []
    for i, entry in enumerate(entries):
        prev_steps = entries[i - 1]["steps"] if i > 0 else None
        change = (entry["steps"] - prev_steps) if prev_steps is not None else None
        result.append(StepsHistoryItem(
            date=entry["date"],
            time=entry["time"],
            steps=entry["steps"],
            change_steps=change,
        ))

    result.reverse()
    return result
