"""
Business logic for daily missions / tasks.

Tabs used:
    Tasks           — task definitions, one row per task type per user.
    DailyTaskStatus — one row per task per day, tracks completion.

Public functions:
    get_today_tasks       — get (or generate) today's mission list.
    complete_task         — mark a specific task complete by task_id + date.
    auto_complete_task    — mark a task complete by task_type; no-op if done.
    check_nutrition_targets — check protein + calorie targets after meal save.
    get_status            — alias for get_today_tasks (summary use).

Private helpers:
    _seed_tasks           — write default task definitions for a new user.
    _ensure_daily_status  — create DailyTaskStatus rows if missing (idempotent).
    _build_response       — build DailyStatusResponse from rows.
    _is_workout_day       — check if today is a workout day for the user.
"""

from __future__ import annotations

import uuid
from datetime import date as date_type, datetime, timezone
from zoneinfo import ZoneInfo

import gspread.exceptions

from ..logger import get_logger
from ..models.task import CompleteTaskRequest, DailyStatusResponse, TaskResponse
from ..sheets.sheets_repo import append_row, append_rows_batch, read_rows, to_int, update_row

logger = get_logger("task_service")

TASKS_TAB = "Tasks"
DAILY_STATUS_TAB = "DailyTaskStatus"
SCHEDULES_TAB = "WorkoutSchedules"

# Default task definitions seeded on first call for a new user.
# Order determines display order in the UI.
DEFAULT_TASKS: list[dict] = [
    {
        "name": "Log your weight",
        "description": "Weigh in and record today's weight",
        "task_type": "log_weight",
    },
    {
        "name": "Hit protein target",
        "description": "Consume at least your daily protein goal",
        "task_type": "hit_protein",
    },
    {
        "name": "Stay under calorie target",
        "description": "Keep daily calories at or below your target",
        "task_type": "stay_under_calories",
    },
    {
        "name": "Complete today's workout",
        "description": "Finish your scheduled workout session",
        "task_type": "complete_workout",
    },
    {
        "name": "Drink enough water",
        "description": "Stay hydrated throughout the day",
        "task_type": "drink_water",
    },
]


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_today_tasks(user_id: int, tz_str: str = "UTC") -> DailyStatusResponse:
    """
    Return today's mission list, generating it if it doesn't exist yet.

    Resolves "today" using the provided timezone string. The ``complete_workout``
    task is omitted on rest days (no workout scheduled for today's weekday).

    Args:
        user_id: Authenticated user's integer ID.
        tz_str: IANA timezone string (e.g. ``"America/Toronto"``).

    Returns:
        ``DailyStatusResponse`` with all tasks and their completion states.
    """
    today = _resolve_today(tz_str)
    task_rows = _get_task_definitions(user_id)
    _ensure_daily_status(user_id, today, task_rows)
    status_rows = _read_daily_status(user_id, today)
    return _build_response(today, task_rows, status_rows, user_id)


def complete_task(user_id: int, task_id: str, date: str) -> DailyStatusResponse:
    """
    Mark a specific task complete for a given date.

    Finds the ``DailyTaskStatus`` row matching ``user_id + task_id + date``
    and sets ``completed=True`` and ``completed_at`` to the current UTC time.
    If already complete, returns the current state without re-writing.

    Args:
        user_id: Authenticated user's integer ID.
        task_id: The task definition ID from the ``Tasks`` tab.
        date: The date to mark complete (``YYYY-MM-DD``).

    Returns:
        Updated ``DailyStatusResponse`` for that date.
    """
    # Ensure tasks exist for this date
    task_rows = _get_task_definitions(user_id)
    _ensure_daily_status(user_id, date, task_rows)

    try:
        status_rows = read_rows(DAILY_STATUS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        status_rows = []

    now = datetime.now(timezone.utc).isoformat()

    for i, row in enumerate(status_rows):
        if (
            to_int(row.get("user_id"), -1) == user_id
            and row.get("task_id") == task_id
            and row.get("date") == date
        ):
            if row.get("completed") == "TRUE":
                break  # Already done — skip redundant write
            updated = {**row, "completed": "TRUE", "completed_at": now}
            row_index = i + 2  # +1 for header, +1 for 0-based → 1-based
            update_row(DAILY_STATUS_TAB, row_index, updated)
            logger.info("Task %s completed for user_id=%s date=%s", task_id, user_id, date)
            break

    updated_status = _read_daily_status(user_id, date)
    return _build_response(date, task_rows, updated_status, user_id)


def auto_complete_task(user_id: int, task_type: str, date: str) -> None:
    """
    Mark a task complete by its type rather than its ID.

    Called automatically from other routers after trigger events (weight logged,
    workout completed). Silently no-ops if the task is already done or if no
    task definition exists for this type and user.

    Args:
        user_id: Authenticated user's integer ID.
        task_type: One of the default task type keys (e.g. ``"log_weight"``).
        date: The date to mark complete (``YYYY-MM-DD``).
    """
    try:
        task_rows = _get_task_definitions(user_id)
        task_id: str | None = None
        for t in task_rows:
            if t.get("task_type") == task_type:
                task_id = str(t.get("id", ""))
                break

        if not task_id:
            logger.warning("No task definition for task_type=%s user_id=%s", task_type, user_id)
            return

        _ensure_daily_status(user_id, date, task_rows)

        try:
            status_rows = read_rows(DAILY_STATUS_TAB)
        except gspread.exceptions.WorksheetNotFound:
            return

        now = datetime.now(timezone.utc).isoformat()
        for i, row in enumerate(status_rows):
            if (
                to_int(row.get("user_id"), -1) == user_id
                and row.get("task_id") == task_id
                and row.get("date") == date
            ):
                if row.get("completed") == "TRUE":
                    return  # Already done
                updated = {**row, "completed": "TRUE", "completed_at": now}
                row_index = i + 2
                update_row(DAILY_STATUS_TAB, row_index, updated)
                logger.info(
                    "Auto-completed task_type=%s for user_id=%s date=%s",
                    task_type, user_id, date,
                )
                return

    except Exception:
        logger.exception(
            "auto_complete_task failed for user_id=%s task_type=%s date=%s",
            user_id, task_type, date,
        )


def check_nutrition_targets(user_id: int, tz_str: str = "UTC") -> None:
    """
    Check if protein and calorie targets have been met; auto-complete those tasks.

    Imports lazily to avoid circular imports (meal_service → task_service
    would create a cycle if task_service imported meal_service at module level).

    Args:
        user_id: Authenticated user's integer ID.
        tz_str: IANA timezone string for resolving "today".
    """
    try:
        from ..services.meal_service import get_meals_today
        from ..services.settings_service import get_settings

        today = _resolve_today(tz_str)
        settings = get_settings(user_id)
        if settings is None:
            return

        nutrition = get_meals_today(user_id, tz_str)

        if nutrition.protein_g >= settings.protein_target_g:
            auto_complete_task(user_id, "hit_protein", today)

        if nutrition.calories <= settings.calorie_target:
            auto_complete_task(user_id, "stay_under_calories", today)

    except Exception:
        logger.exception("check_nutrition_targets failed for user_id=%s", user_id)


def get_status(user_id: int, tz_str: str = "UTC") -> DailyStatusResponse:
    """Alias for ``get_today_tasks`` — returns today's mission summary."""
    return get_today_tasks(user_id, tz_str)


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _resolve_today(tz_str: str) -> str:
    """Return today's date in ``YYYY-MM-DD`` format for the given timezone."""
    try:
        from datetime import timezone as _tz
        if tz_str.upper() == "UTC":
            return datetime.now(_tz.utc).date().isoformat()
        tz = ZoneInfo(tz_str)
        return datetime.now(tz).date().isoformat()
    except Exception:
        return date_type.today().isoformat()


def _get_task_definitions(user_id: int) -> list[dict]:
    """
    Return existing task definition rows for this user, seeding defaults if none exist.
    """
    try:
        rows = read_rows(TASKS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        rows = []

    user_tasks = [r for r in rows if to_int(r.get("user_id"), -1) == user_id]
    if not user_tasks:
        user_tasks = _seed_tasks(user_id)
    return user_tasks


def _seed_tasks(user_id: int) -> list[dict]:
    """Write default task definitions for a new user and return them."""
    rows = []
    for t in DEFAULT_TASKS:
        row = {
            "user_id": user_id,
            "id": str(uuid.uuid4()),
            "name": t["name"],
            "description": t["description"],
            "task_type": t["task_type"],
        }
        rows.append(row)

    try:
        append_rows_batch(TASKS_TAB, rows)
    except Exception:
        logger.exception("Failed to seed tasks for user_id=%s", user_id)

    logger.info("Seeded %d task definitions for user_id=%s", len(rows), user_id)
    return rows


def _ensure_daily_status(user_id: int, date: str, task_rows: list[dict]) -> None:
    """
    Create DailyTaskStatus rows for ``date`` if they don't already exist.

    Idempotent — calling twice for the same date produces the same rows.
    Skips the ``complete_workout`` task on rest days to avoid showing it.
    """
    try:
        existing = read_rows(DAILY_STATUS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        existing = []

    existing_task_ids = {
        r.get("task_id")
        for r in existing
        if to_int(r.get("user_id"), -1) == user_id and r.get("date") == date
    }

    is_rest = _is_rest_day(user_id, date)

    rows_to_add = []
    for t in task_rows:
        task_id = str(t.get("id", ""))
        task_type = str(t.get("task_type", ""))

        # Skip workout task on rest days
        if task_type == "complete_workout" and is_rest:
            continue

        if task_id in existing_task_ids:
            continue  # Already exists for this date

        rows_to_add.append({
            "user_id": user_id,
            "id": str(uuid.uuid4()),
            "task_id": task_id,
            "date": date,
            "completed": "FALSE",
            "completed_at": "",
        })

    if rows_to_add:
        try:
            append_rows_batch(DAILY_STATUS_TAB, rows_to_add)
            logger.info(
                "Created %d DailyTaskStatus rows for user_id=%s date=%s",
                len(rows_to_add), user_id, date,
            )
        except Exception:
            logger.exception(
                "Failed to create DailyTaskStatus rows for user_id=%s date=%s",
                user_id, date,
            )


def _read_daily_status(user_id: int, date: str) -> list[dict]:
    """Return DailyTaskStatus rows for this user and date."""
    try:
        rows = read_rows(DAILY_STATUS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return []
    return [
        r for r in rows
        if to_int(r.get("user_id"), -1) == user_id and r.get("date") == date
    ]


def _compute_streak(user_id: int, today: str) -> int:
    """
    Count consecutive fully-complete days ending on or before ``today``.

    Scans all ``DailyTaskStatus`` rows for the user. A day counts toward the
    streak only if every task scheduled for that day was completed. Days with
    zero tasks are not counted. The streak walks backwards from yesterday (or
    today if today is already fully complete) until a gap is found.

    Args:
        user_id: Authenticated user's integer ID.
        today: Today's date string (``YYYY-MM-DD``), used as the end bound.

    Returns:
        Integer streak count, 0 if no consecutive complete days exist.
    """
    try:
        rows = read_rows(DAILY_STATUS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return 0

    user_rows = [r for r in rows if to_int(r.get("user_id"), -1) == user_id]
    if not user_rows:
        return 0

    # Group by date: {date -> {total, completed}}
    by_date: dict[str, dict] = {}
    for r in user_rows:
        d = r.get("date", "")
        if not d:
            continue
        entry = by_date.setdefault(d, {"total": 0, "completed": 0})
        entry["total"] += 1
        if r.get("completed") == "TRUE":
            entry["completed"] += 1

    # Walk backwards from today, counting consecutive complete days.
    # Today still being in progress must not break an existing streak, so if
    # today is not (yet) fully complete the walk starts from yesterday instead.
    from datetime import timedelta

    def _is_complete(key: str) -> bool:
        day = by_date.get(key)
        return day is not None and day["total"] > 0 and day["completed"] >= day["total"]

    streak = 0
    check = date_type.fromisoformat(today)
    if not _is_complete(check.isoformat()):
        check -= timedelta(days=1)
    while _is_complete(check.isoformat()):
        streak += 1
        check -= timedelta(days=1)

    return streak


def _build_response(
    date: str,
    task_rows: list[dict],
    status_rows: list[dict],
    user_id: int | None = None,
) -> DailyStatusResponse:
    """Combine task definitions with daily status rows into a response object."""
    status_by_task_id = {r["task_id"]: r for r in status_rows if r.get("task_id")}

    tasks: list[TaskResponse] = []
    for t in task_rows:
        task_id = str(t.get("id", ""))
        status = status_by_task_id.get(task_id)
        if status is None:
            # Task was skipped (e.g. workout on rest day) — omit from response
            continue
        completed = status.get("completed", "FALSE") == "TRUE"
        completed_at = status.get("completed_at") or None
        tasks.append(
            TaskResponse(
                id=task_id,
                name=str(t.get("name", "")),
                description=str(t.get("description", "")),
                task_type=str(t.get("task_type", "")),
                completed=completed,
                completed_at=completed_at,
            )
        )

    total = len(tasks)
    completed_count = sum(1 for t in tasks if t.completed)
    percentage = round((completed_count / total * 100) if total > 0 else 0.0, 1)
    streak = _compute_streak(user_id, date) if user_id is not None else 0

    return DailyStatusResponse(
        date=date,
        tasks=tasks,
        total=total,
        completed=completed_count,
        percentage=percentage,
        streak=streak,
    )


def _is_rest_day(user_id: int, date_str: str) -> bool:
    """
    Return True if the given date has no workout scheduled (rest day or no schedule).

    Filters WorkoutSchedules by the user's active plan so that switching plans
    immediately reflects on which days show the "complete workout" mission.
    Falls back gracefully if WorkoutPlans tab does not exist yet (legacy mode).
    """
    try:
        from .workout_service import get_active_plan_id

        weekday = date_type.fromisoformat(date_str).weekday()  # 0=Mon
        rows = read_rows(SCHEDULES_TAB)
        active_plan_id = get_active_plan_id(user_id)

        for r in rows:
            if to_int(r.get("user_id"), -1) != user_id:
                continue
            # If we have an active plan, filter to its rows; skip rows from other plans
            if active_plan_id is not None and str(r.get("plan_id", "")) != active_plan_id:
                continue
            if to_int(r.get("weekday"), -1) == weekday:
                day_name = str(r.get("day_name", ""))
                return day_name == "Rest" or not day_name
        # No schedule row found → treat as rest day
        return True
    except Exception:
        return True  # Default to rest day if anything fails
