"""
Business logic for meal tracking.

Reads from and writes to the ``Meals`` and ``MealItems`` tabs of the Main
Data Sheet.  Each ``Meals`` row is one meal (one camera capture + confirm).
Each ``MealItems`` row is one detected food item belonging to a meal.

Public functions:
    save_meal       — append a confirmed meal + its items to the sheets.
    get_meals_today — return all meals logged today with daily totals.
    get_meals_history — per-day summary for the last N days.

The ``DailyNutrition`` returned by ``get_meals_today`` includes target values
derived from the user's ``Settings`` row so the frontend can render progress
bars without a separate settings fetch.
"""

from __future__ import annotations

import uuid
from datetime import date as date_type, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import gspread.exceptions

from ..logger import get_logger
from ..models.meal import (
    ConfirmMealRequest,
    DailyNutrition,
    DetectedItem,
    MacroTotal,
    MealHistoryDay,
    MealRecord,
    SavedMealResponse,
)
from ..services.settings_service import get_settings
from ..sheets.sheets_repo import append_row, append_rows_batch, read_rows

logger = get_logger("meal_service")

MEALS_TAB = "Meals"
MEAL_ITEMS_TAB = "MealItems"


# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------


def save_meal(user_id: int, confirm: ConfirmMealRequest, tz_str: str = "UTC") -> SavedMealResponse:
    """
    Persist a confirmed meal and its items to the Sheets.

    Appends one row to ``Meals`` and N rows to ``MealItems`` (one per detected
    item). The ``meal_id`` is generated as a UUID string.  After saving, the
    updated daily nutrition totals are fetched and included in the response.

    Args:
        user_id: Authenticated user's integer ID.
        confirm: The user-confirmed meal payload from ``POST /meals``.
        tz_str: IANA timezone string from ``X-Timezone`` request header.
            Used to resolve "today" for the daily nutrition fetch.

    Returns:
        ``SavedMealResponse`` with the new meal's ID, type, totals, and the
        updated ``DailyNutrition`` for the day.
    """
    meal_id = str(uuid.uuid4())
    now_utc = datetime.now(timezone.utc)
    logged_at = now_utc.isoformat()
    # Derive the displayed clock time in the user's local timezone so meal
    # records show the correct local time rather than the server's UTC clock.
    try:
        _tz = ZoneInfo(tz_str)
    except Exception:
        _tz = ZoneInfo("UTC")
    entry_time = datetime.now(_tz).strftime("%H:%M")

    total = MacroTotal(
        calories=sum(it.calories for it in confirm.items),
        protein_g=round(sum(it.protein_g for it in confirm.items), 1),
        carbs_g=round(sum(it.carbs_g for it in confirm.items), 1),
        fat_g=round(sum(it.fat_g for it in confirm.items), 1),
    )

    # Derive a short title from the meal type + item names
    title = _make_title(confirm.items)

    meal_row = {
        "meal_id": meal_id,
        "user_id": user_id,
        "date": confirm.date,
        "time": entry_time,
        "meal_type": confirm.meal_type,
        "title": title,
        "drive_url": confirm.drive_url,
        "total_calories": total.calories,
        "total_protein_g": total.protein_g,
        "total_carbs_g": total.carbs_g,
        "total_fat_g": total.fat_g,
        "item_count": len(confirm.items),
        "logged_at": logged_at,
    }
    logger.info(
        "Saving meal user_id=%s date=%s type=%s items=%s cal=%s",
        user_id,
        confirm.date,
        confirm.meal_type,
        len(confirm.items),
        total.calories,
    )
    append_row(MEALS_TAB, meal_row)

    item_rows = [
        {
            "meal_id": meal_id,
            "user_id": user_id,
            "date": confirm.date,
            "name": it.name,
            "quantity": it.quantity,
            "calories": it.calories,
            "protein_g": it.protein_g,
            "carbs_g": it.carbs_g,
            "fat_g": it.fat_g,
            "confidence": it.confidence,
        }
        for it in confirm.items
    ]
    append_rows_batch(MEAL_ITEMS_TAB, item_rows)

    daily = get_meals_today(user_id, tz_str)
    return SavedMealResponse(
        meal_id=meal_id,
        meal_type=confirm.meal_type,
        date=confirm.date,
        total=total,
        daily_nutrition=daily,
    )


# ---------------------------------------------------------------------------
# Today
# ---------------------------------------------------------------------------


def get_meals_today(user_id: int, tz_str: str = "UTC") -> DailyNutrition:
    """
    Return today's meals summed into a ``DailyNutrition`` object.

    Resolves "today" using the ``tz_str`` timezone so that users in different
    time zones see the correct date boundary.  Nutrition targets come from the
    user's ``Settings`` row — missing settings produce zero targets.

    Args:
        user_id: Authenticated user's integer ID.
        tz_str: IANA timezone string (e.g. ``"America/New_York"``).

    Returns:
        ``DailyNutrition`` with consumed and target values for today.
    """
    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        tz = ZoneInfo("UTC")

    today = datetime.now(tz).strftime("%Y-%m-%d")

    try:
        meal_rows = read_rows(MEALS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        meal_rows = []

    today_meals = [
        r for r in meal_rows
        if str(r.get("user_id", "")) == str(user_id) and r.get("date") == today
    ]

    cals = sum(int(r.get("total_calories", 0)) for r in today_meals)
    protein = sum(float(r.get("total_protein_g", 0)) for r in today_meals)
    carbs = sum(float(r.get("total_carbs_g", 0)) for r in today_meals)
    fat = sum(float(r.get("total_fat_g", 0)) for r in today_meals)

    target_cals, target_protein, target_carbs, target_fat = _get_targets(user_id)

    return DailyNutrition(
        date=today,
        calories=cals,
        protein_g=round(protein, 1),
        carbs_g=round(carbs, 1),
        fat_g=round(fat, 1),
        target_calories=target_cals,
        target_protein_g=target_protein,
        target_carbs_g=target_carbs,
        target_fat_g=target_fat,
        meals_count=len(today_meals),
    )


# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------


def get_meals_history(user_id: int, days: int = 30, tz_str: str = "UTC") -> list[MealHistoryDay]:
    """
    Return per-day nutrition summaries for the last ``days`` calendar days.

    The returned list is sorted newest first. Days with no meals are omitted.
    "Today" and "Yesterday" labels are computed in the user's local timezone.

    Args:
        user_id: Authenticated user's integer ID.
        days: Number of calendar days to look back. Defaults to 30.
        tz_str: IANA timezone string (e.g. ``"Asia/Kolkata"``). Used to determine
            which calendar date is "today" for display labels.

    Returns:
        List of ``MealHistoryDay`` objects, newest first.
    """
    try:
        _tz = ZoneInfo(tz_str)
    except Exception:
        _tz = ZoneInfo("UTC")

    today_str = datetime.now(_tz).date().isoformat()
    yesterday_str = (datetime.now(_tz).date() - timedelta(days=1)).isoformat()
    cutoff = (datetime.now(_tz).date() - timedelta(days=days)).isoformat()

    try:
        meal_rows = read_rows(MEALS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return []

    user_meals = [
        r for r in meal_rows
        if str(r.get("user_id", "")) == str(user_id) and r.get("date", "") >= cutoff
    ]

    # Group by date
    by_date: dict[str, dict] = {}
    for r in user_meals:
        d = r.get("date", "")
        if d not in by_date:
            by_date[d] = {"total_calories": 0, "total_protein_g": 0.0, "count": 0}
        by_date[d]["total_calories"] += int(r.get("total_calories", 0))
        by_date[d]["total_protein_g"] += float(r.get("total_protein_g", 0))
        by_date[d]["count"] += 1

    result = []
    for d in sorted(by_date.keys(), reverse=True):
        info = by_date[d]
        if d == today_str:
            display = f"Today · {_fmt_date(d)}"
        elif d == yesterday_str:
            display = f"Yesterday · {_fmt_date(d)}"
        else:
            display = f"{_weekday_short(d)} · {_fmt_date(d)}"
        result.append(
            MealHistoryDay(
                date=d,
                display_date=display,
                meals_count=info["count"],
                total_calories=info["total_calories"],
                total_protein_g=round(info["total_protein_g"], 1),
            )
        )
    return result


# ---------------------------------------------------------------------------
# Read individual meals (used by agent tools)
# ---------------------------------------------------------------------------


def get_meal_records_today(user_id: int, tz_str: str = "UTC") -> list[MealRecord]:
    """
    Return full meal records for today including items.

    Args:
        user_id: Authenticated user's integer ID.
        tz_str: IANA timezone string.

    Returns:
        List of ``MealRecord`` objects for today, oldest first.
    """
    try:
        tz = ZoneInfo(tz_str)
    except Exception:
        tz = ZoneInfo("UTC")
    today = datetime.now(tz).strftime("%Y-%m-%d")

    try:
        meal_rows = read_rows(MEALS_TAB)
        item_rows = read_rows(MEAL_ITEMS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return []

    today_meals = sorted(
        [
            r for r in meal_rows
            if str(r.get("user_id", "")) == str(user_id) and r.get("date") == today
        ],
        key=lambda r: r.get("logged_at", ""),
    )

    items_by_meal: dict[str, list[DetectedItem]] = {}
    for it in item_rows:
        mid = str(it.get("meal_id", ""))
        if mid not in items_by_meal:
            items_by_meal[mid] = []
        items_by_meal[mid].append(
            DetectedItem(
                name=str(it.get("name", "")),
                quantity=str(it.get("quantity", "")),
                calories=int(it.get("calories", 0)),
                protein_g=float(it.get("protein_g", 0)),
                carbs_g=float(it.get("carbs_g", 0)),
                fat_g=float(it.get("fat_g", 0)),
                confidence=it.get("confidence", "med"),  # type: ignore[arg-type]
            )
        )

    records = []
    for r in today_meals:
        mid = str(r.get("meal_id", ""))
        total = MacroTotal(
            calories=int(r.get("total_calories", 0)),
            protein_g=float(r.get("total_protein_g", 0)),
            carbs_g=float(r.get("total_carbs_g", 0)),
            fat_g=float(r.get("total_fat_g", 0)),
        )
        records.append(
            MealRecord(
                meal_id=mid,
                user_id=user_id,
                date=str(r.get("date", "")),
                time=str(r.get("time", "")),
                meal_type=r.get("meal_type", "Snack"),  # type: ignore[arg-type]
                title=str(r.get("title", "")),
                drive_url=str(r.get("drive_url", "")),
                total=total,
                items=items_by_meal.get(mid, []),
            )
        )
    return records


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _get_targets(user_id: int) -> tuple[int, float, float, float]:
    """Return (calorie_target, protein_g, carbs_g, fat_g) from Settings."""
    settings = get_settings(user_id)
    if not settings:
        return 2000, 150.0, 200.0, 65.0

    cal = settings.calorie_target
    pro = float(settings.protein_target_g)
    protein_kcal = pro * 4
    remaining = max(cal - protein_kcal, 0)
    # Split remaining ≈ 55% carbs, 45% fat
    carbs = round((remaining * 0.55) / 4, 1)
    fat = round((remaining * 0.45) / 9, 1)
    return cal, pro, carbs, fat


def _make_title(items: list[DetectedItem]) -> str:
    """Build a short title from the first 1–3 item names."""
    names = [it.name for it in items[:3]]
    if not names:
        return "Meal"
    title = ", ".join(names)
    if len(items) > 3:
        title += f" +{len(items) - 3}"
    return title


def _fmt_date(date_str: str) -> str:
    """Format YYYY-MM-DD as 'Jun 5'."""
    try:
        d = date_type.fromisoformat(date_str)
        return d.strftime("%b %-d")
    except Exception:
        return date_str


def _weekday_short(date_str: str) -> str:
    """Return 3-letter weekday name e.g. 'Mon'."""
    try:
        return date_type.fromisoformat(date_str).strftime("%a")
    except Exception:
        return ""
