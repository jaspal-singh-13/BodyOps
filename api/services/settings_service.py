from datetime import datetime, timezone
from typing import Any

import gspread.exceptions

from ..models.settings import SettingsCreate, SettingsResponse
from ..sheets.sheets_repo import append_row, find_row, read_rows, update_row

SETTINGS_TAB = "Settings"


def get_settings(user_id: int) -> SettingsResponse | None:
    try:
        rows = read_rows(SETTINGS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return None
    row: dict[str, Any] | None = next(
        (r for r in rows if int(r.get("user_id", -1)) == user_id), None
    )
    if row is None:
        return None
    return SettingsResponse(
        user_id=int(row.get("user_id", 0)),
        name=str(row.get("name", "")),
        current_weight_kg=float(row.get("current_weight_kg", 0)),
        height_cm=float(row.get("height_cm", 0)),
        age=int(row.get("age", 0)),
        goal_weight_kg=float(row.get("goal_weight_kg", 0)),
        start_date=str(row.get("start_date", "")),
        calorie_target=int(row.get("calorie_target", 0)),
        protein_target_g=int(row.get("protein_target_g", 0)),
        wake_up_time=str(row.get("wake_up_time", "07:00")),
        unit_preference=str(row.get("unit_preference", "metric")),
        reminders_json=str(row.get("reminders_json", "{}")),
        updated_at=str(row.get("updated_at", "")),
    )


def save_settings(user_id: int, data: SettingsCreate) -> SettingsResponse:
    now = datetime.now(timezone.utc).isoformat()
    row_dict = {"user_id": user_id, **data.model_dump(exclude={"user_id"}), "updated_at": now}
    try:
        result = find_row(SETTINGS_TAB, "user_id", str(user_id))
    except gspread.exceptions.WorksheetNotFound:
        result = None
    if result is not None:
        row_index, _ = result
        update_row(SETTINGS_TAB, row_index, row_dict)
    else:
        append_row(SETTINGS_TAB, row_dict)
    return SettingsResponse(**row_dict)
