"""
Workout service — business logic for Phase 3 + plan library.

Tabs used:
    WorkoutPlans     — one row per saved plan per user; one row has is_active=TRUE
    WorkoutPrograms  — one row per exercise per workout day, scoped by plan_id
    WorkoutSchedules — one row per weekday (0=Mon … 6=Sun), scoped by plan_id
    WorkoutSessions  — one row per session (auto-created on first set log)
    WorkoutSets      — one row per set logged

Legacy fallback:
    Users who have WorkoutPrograms/WorkoutSchedules rows but no WorkoutPlans row
    (i.e. before running migrate_add_plan_id.py) are handled transparently:
    get_active_plan_id() returns None, and _filter_by_plan() with plan_id=None
    falls back to filtering by user_id only — matching the pre-library behaviour.
"""

from __future__ import annotations

import asyncio
import math
from datetime import date, datetime, timezone
from typing import Any

import gspread.exceptions

from ..logger import get_logger
from ..models.workout import (
    ExerciseInfo,
    ExerciseProgressionResponse,
    LogSetRequest,
    LogSetResponse,
    ProgressionSuggestion,
    ScheduleDay,
    TodayExercise,
    TodayWorkoutResponse,
    WorkoutDaySummary,
    WorkoutHistoryResponse,
    WorkoutImportResponse,
    WorkoutPlanSummary,
    WorkoutPlansResponse,
    WorkoutScheduleResponse,
)
from ..sheets.sheets_client import get_worksheet
from ..sheets.sheets_repo import append_row, append_rows_batch, read_rows, update_row

PLANS_TAB = "WorkoutPlans"
PROGRAMS_TAB = "WorkoutPrograms"
SCHEDULES_TAB = "WorkoutSchedules"
SESSIONS_TAB = "WorkoutSessions"
SETS_TAB = "WorkoutSets"

logger = get_logger("workout_service")


# ---------------------------------------------------------------------------
# Progressive overload — pure function (also tested in test_progression.py)
# ---------------------------------------------------------------------------


def compute_suggestion(
    exercise_name: str,
    rep_min: int,
    rep_max: int,
    last_weight_kg: float | None,
    last_reps: int | None,
) -> ProgressionSuggestion:
    if last_weight_kg is None or last_reps is None:
        return ProgressionSuggestion(weight_kg=None, reps=None, note="first session")

    rep_mid = (rep_min + rep_max) / 2

    if last_reps >= rep_max:
        return ProgressionSuggestion(
            weight_kg=round(last_weight_kg + 2.5, 1),
            reps=rep_min,
            note="increase weight",
        )
    elif last_reps >= rep_mid:
        return ProgressionSuggestion(
            weight_kg=last_weight_kg,
            reps=last_reps + 1,
            note="add rep",
        )
    else:
        return ProgressionSuggestion(
            weight_kg=max(0.0, round(last_weight_kg - 2.5, 1)),
            reps=last_reps,
            note="reduce weight",
        )


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat()


def _safe_read_rows(tab: str) -> list[dict[str, Any]]:
    """Read all rows from a tab, returning [] if the tab doesn't exist."""
    try:
        return read_rows(tab)
    except gspread.exceptions.WorksheetNotFound:
        return []


def _group_contiguous(indices: list[int]) -> list[tuple[int, int]]:
    """Group a sorted list of 1-based row indices into contiguous (start, end) ranges."""
    if not indices:
        return []
    ranges: list[tuple[int, int]] = []
    start = end = indices[0]
    for idx in indices[1:]:
        if idx == end + 1:
            end = idx
        else:
            ranges.append((start, end))
            start = end = idx
    ranges.append((start, end))
    return ranges


def _delete_user_rows(tab: str, user_id: int) -> None:
    """
    Delete all rows belonging to user_id in the given tab.

    Groups contiguous row indices into ranges and issues one delete call per
    range (in reverse order to preserve row indices), reducing N individual
    API calls to typically 1–2 for a single-user dataset.
    """
    try:
        ws = get_worksheet(tab)
    except gspread.exceptions.WorksheetNotFound:
        return
    records = ws.get_all_records()
    indices = sorted(
        i + 2  # +1 for header row, +1 for 0-based → 1-based
        for i, r in enumerate(records)
        if int(r.get("user_id", -1)) == user_id
    )
    if not indices:
        return
    for start, end in reversed(_group_contiguous(indices)):
        ws.delete_rows(start, end)


def _delete_plan_rows(tab: str, user_id: int, plan_id: str) -> None:
    """Delete all rows matching (user_id, plan_id) in the given tab."""
    try:
        ws = get_worksheet(tab)
    except gspread.exceptions.WorksheetNotFound:
        return
    records = ws.get_all_records()
    indices = sorted(
        i + 2
        for i, r in enumerate(records)
        if int(r.get("user_id", -1)) == user_id and str(r.get("plan_id", "")) == plan_id
    )
    if not indices:
        return
    for start, end in reversed(_group_contiguous(indices)):
        ws.delete_rows(start, end)


def _filter_by_plan(
    rows: list[dict[str, Any]],
    user_id: int,
    plan_id: str | None,
) -> list[dict[str, Any]]:
    """
    Filter rows by user_id and optionally by plan_id.

    When plan_id is None (legacy mode — no WorkoutPlans row exists), only
    user_id is applied so existing data behaves exactly as before the
    plan library was introduced.
    """
    user_rows = [r for r in rows if int(r.get("user_id", -1)) == user_id]
    if plan_id is None:
        return user_rows
    return [r for r in user_rows if str(r.get("plan_id", "")) == plan_id]


def _get_last_set_from_rows(
    set_rows: list[dict[str, Any]],
    user_id: int,
    exercise_name: str,
) -> tuple[float | None, int | None]:
    """
    Return (weight_kg, reps) from the final set of the most recent session.

    Operates on a pre-loaded list of rows — no additional Sheets I/O.
    Progression is intentionally cross-plan (history follows the exercise,
    not the plan).
    """
    user_rows = [
        r for r in set_rows
        if int(r.get("user_id", -1)) == user_id
        and r.get("exercise_name", "") == exercise_name
    ]
    if not user_rows:
        return None, None

    user_rows.sort(key=lambda r: r.get("logged_at", ""), reverse=True)
    most_recent_session = user_rows[0].get("session_id", "")
    session_rows = [r for r in user_rows if r.get("session_id") == most_recent_session]
    last_row = max(session_rows, key=lambda r: int(r.get("set_number", 0)))
    return float(last_row["weight_kg"]), int(last_row["reps"])


def _get_last_set(user_id: int, exercise_name: str) -> tuple[float | None, int | None]:
    """Return (weight_kg, reps) from the final set of the most recent session."""
    return _get_last_set_from_rows(_safe_read_rows(SETS_TAB), user_id, exercise_name)


def _get_program_rep_range_from_rows(
    program_rows: list[dict[str, Any]],
    user_id: int,
    exercise_name: str,
) -> tuple[int, int]:
    """
    Look up rep_min/rep_max from pre-loaded WorkoutPrograms rows; fall back to (8, 12).

    Operates on a pre-loaded list of rows — no additional Sheets I/O.
    Expects rows already filtered to the active plan (or all user rows in legacy mode).
    """
    for r in program_rows:
        if (
            int(r.get("user_id", -1)) == user_id
            and r.get("exercise_name", "") == exercise_name
        ):
            return int(r["rep_min"]), int(r["rep_max"])
    return 8, 12


def _get_program_rep_range(user_id: int, exercise_name: str) -> tuple[int, int]:
    """Look up rep_min/rep_max from the active plan's WorkoutPrograms; fall back to (8, 12)."""
    active_plan_id = get_active_plan_id(user_id)
    program_rows = _filter_by_plan(_safe_read_rows(PROGRAMS_TAB), user_id, active_plan_id)
    return _get_program_rep_range_from_rows(program_rows, user_id, exercise_name)


# ---------------------------------------------------------------------------
# Plan management
# ---------------------------------------------------------------------------


def get_active_plan_id(user_id: int) -> str | None:
    """
    Return the plan_id of the user's currently active plan, or None.

    None means the user has no WorkoutPlans row (legacy / un-migrated state).
    Callers that receive None should fall back to filtering by user_id only.
    """
    rows = _safe_read_rows(PLANS_TAB)
    for r in rows:
        if (
            int(r.get("user_id", -1)) == user_id
            and str(r.get("is_active", "")).upper() == "TRUE"
        ):
            return str(r["plan_id"])
    return None


def list_plans(user_id: int) -> WorkoutPlansResponse:
    """Return all saved plans for the user with name, active flag, and day/exercise counts."""
    plan_rows = _safe_read_rows(PLANS_TAB)
    program_rows = _safe_read_rows(PROGRAMS_TAB)

    user_plans = [r for r in plan_rows if int(r.get("user_id", -1)) == user_id]
    summaries: list[WorkoutPlanSummary] = []

    for r in user_plans:
        plan_id = str(r.get("plan_id", ""))
        plan_name = str(r.get("plan_name", ""))
        is_active = str(r.get("is_active", "")).upper() == "TRUE"
        created_at = str(r.get("created_at", ""))

        plan_programs = [
            p for p in program_rows
            if int(p.get("user_id", -1)) == user_id
            and str(p.get("plan_id", "")) == plan_id
            and p.get("exercise_name", "")
        ]
        exercise_count = len(plan_programs)
        day_count = len({p["day_name"] for p in plan_programs})

        summaries.append(WorkoutPlanSummary(
            plan_id=plan_id,
            plan_name=plan_name,
            is_active=is_active,
            day_count=day_count,
            exercise_count=exercise_count,
            created_at=created_at,
        ))

    return WorkoutPlansResponse(plans=summaries)


def activate_plan(user_id: int, plan_id: str) -> None:
    """
    Make the given plan the active one for the user.

    Deactivates the current active plan, then activates the target.
    Raises ValueError if the plan_id does not exist for this user.
    """
    plan_rows = _safe_read_rows(PLANS_TAB)

    target_idx: int | None = None
    rows_to_deactivate: list[tuple[int, dict]] = []

    for i, r in enumerate(plan_rows):
        if int(r.get("user_id", -1)) != user_id:
            continue
        row_index = i + 2  # 1-based + header
        if str(r.get("plan_id", "")) == plan_id:
            target_idx = row_index
            target_row = dict(r)
        elif str(r.get("is_active", "")).upper() == "TRUE":
            rows_to_deactivate.append((row_index, dict(r)))

    if target_idx is None:
        raise ValueError(f"Plan '{plan_id}' not found for user {user_id}")

    for row_index, row in rows_to_deactivate:
        row["is_active"] = "FALSE"
        update_row(PLANS_TAB, row_index, row)

    target_row["is_active"] = "TRUE"
    update_row(PLANS_TAB, target_idx, target_row)
    logger.info("Activated plan %s for user_id=%s", plan_id, user_id)


def delete_plan(user_id: int, plan_id: str) -> None:
    """
    Delete a saved plan and all its programs/schedules.

    Raises ValueError if the plan is currently active (switch first) or not found.
    """
    active_plan_id = get_active_plan_id(user_id)
    if active_plan_id == plan_id:
        raise ValueError("Cannot delete the active plan — switch to another plan first")

    plan_rows = _safe_read_rows(PLANS_TAB)
    plan_row_idx: int | None = None
    for i, r in enumerate(plan_rows):
        if int(r.get("user_id", -1)) == user_id and str(r.get("plan_id", "")) == plan_id:
            plan_row_idx = i + 2
            break

    if plan_row_idx is None:
        raise ValueError(f"Plan '{plan_id}' not found for user {user_id}")

    _delete_plan_rows(PROGRAMS_TAB, user_id, plan_id)
    _delete_plan_rows(SCHEDULES_TAB, user_id, plan_id)

    try:
        ws = get_worksheet(PLANS_TAB)
        ws.delete_rows(plan_row_idx)
    except gspread.exceptions.WorksheetNotFound:
        pass

    logger.info("Deleted plan %s for user_id=%s", plan_id, user_id)


def switch_plan_by_name(user_id: int, plan_name: str) -> dict:
    """
    Resolve plan_name → plan_id case-insensitively and activate it.

    Returns a result dict suitable for returning directly from an agent tool.
    On no match, returns an error dict listing available plan names so the
    model can recover without exposing raw plan_ids.
    """
    plan_rows = _safe_read_rows(PLANS_TAB)
    user_plans = [r for r in plan_rows if int(r.get("user_id", -1)) == user_id]

    target: dict | None = None
    for r in user_plans:
        if str(r.get("plan_name", "")).lower() == plan_name.lower():
            target = r
            break

    if target is None:
        available = [str(r.get("plan_name", "")) for r in user_plans]
        return {
            "error": f"Plan '{plan_name}' not found.",
            "available_plans": available,
        }

    target_plan_id = str(target["plan_id"])
    activate_plan(user_id, target_plan_id)
    return {
        "activated": True,
        "plan_id": target_plan_id,
        "plan_name": str(target.get("plan_name", "")),
    }


def _deactivate_current_plan(user_id: int) -> None:
    """Mark the current active plan as inactive (called before activating a new import)."""
    plan_rows = _safe_read_rows(PLANS_TAB)
    for i, r in enumerate(plan_rows):
        if (
            int(r.get("user_id", -1)) == user_id
            and str(r.get("is_active", "")).upper() == "TRUE"
        ):
            row = dict(r)
            row["is_active"] = "FALSE"
            update_row(PLANS_TAB, i + 2, row)
            return


# ---------------------------------------------------------------------------
# Service functions
# ---------------------------------------------------------------------------


def import_workout(
    user_id: int,
    program_name: str,
    days: list[WorkoutDaySummary],
    schedule: list[tuple[int, str]],
) -> WorkoutImportResponse:
    now = _now_utc()
    now_ms = int(datetime.now(timezone.utc).timestamp() * 1000)
    plan_id = f"{user_id}-{now_ms}"

    # Deactivate any existing active plan (non-destructive — old plan rows kept)
    _deactivate_current_plan(user_id)

    # Register new plan as active
    append_row(PLANS_TAB, {
        "user_id": user_id,
        "plan_id": plan_id,
        "plan_name": program_name,
        "is_active": "TRUE",
        "created_at": now,
    })

    total_exercises = 0
    program_days = 0
    program_rows: list[dict] = []
    schedule_rows: list[dict] = []

    for day in days:
        if day.day_name == "Rest":
            continue
        program_days += 1
        for ex in day.exercises:
            program_rows.append(
                {
                    "user_id": user_id,
                    "plan_id": plan_id,
                    "program_name": program_name,
                    "day_name": day.day_name,
                    "exercise_name": ex.exercise_name,
                    "sets": ex.sets,
                    "rep_min": ex.rep_min,
                    "rep_max": ex.rep_max,
                    "order": ex.order,
                    "created_at": now,
                }
            )
            total_exercises += 1

    # Ensure all 7 weekdays are present — fill gaps with "Rest" so that
    # get_today_workout never returns a rest day just because the AI omitted a day.
    covered_weekdays = {weekday for weekday, _ in schedule}
    full_schedule = list(schedule) + [
        (wd, "Rest") for wd in range(7) if wd not in covered_weekdays
    ]

    for weekday, day_name in full_schedule:
        schedule_rows.append(
            {
                "user_id": user_id,
                "plan_id": plan_id,
                "weekday": weekday,
                "day_name": day_name,
                "created_at": now,
            }
        )

    append_rows_batch(PROGRAMS_TAB, program_rows)
    append_rows_batch(SCHEDULES_TAB, schedule_rows)

    rest_days = sum(1 for d in days if d.day_name == "Rest")
    logger.info(
        "Imported workout plan %s for user_id=%s: %s days, %s exercises",
        plan_id, user_id, program_days, total_exercises,
    )

    return WorkoutImportResponse(
        program_name=program_name,
        program_days=program_days,
        rest_days=rest_days,
        total_exercises=total_exercises,
        days=days,
    )


def get_today_workout(user_id: int, today_date: str) -> TodayWorkoutResponse:
    weekday = date.fromisoformat(today_date).weekday()  # 0=Mon
    active_plan_id = get_active_plan_id(user_id)

    schedule_rows = _safe_read_rows(SCHEDULES_TAB)
    plan_schedule = _filter_by_plan(schedule_rows, user_id, active_plan_id)

    day_name: str | None = None
    for r in plan_schedule:
        if int(r.get("weekday", -1)) == weekday:
            day_name = str(r.get("day_name", "")) or None
            break

    # Resolve plan name
    plan_name: str | None = None
    if active_plan_id is not None:
        plan_rows = _safe_read_rows(PLANS_TAB)
        for r in plan_rows:
            if int(r.get("user_id", -1)) == user_id and str(r.get("plan_id", "")) == active_plan_id:
                plan_name = str(r.get("plan_name", "")) or None
                break

    if day_name is None or day_name == "Rest":
        return TodayWorkoutResponse(
            date=today_date,
            day_name=day_name or "Rest",
            is_rest_day=True,
            exercises=[],
            estimated_duration_min=0,
            session_id=None,
            is_completed=False,
            plan_name=plan_name,
        )

    program_rows = _safe_read_rows(PROGRAMS_TAB)
    plan_programs = _filter_by_plan(program_rows, user_id, active_plan_id)

    ex_rows = sorted(
        [
            r for r in plan_programs
            if r.get("day_name") == day_name
            and r.get("exercise_name")
        ],
        key=lambda r: int(r.get("order", 0)),
    )

    # Read SETS_TAB and SESSIONS_TAB once — eliminates the N+1
    all_set_rows = _safe_read_rows(SETS_TAB)
    session_rows = _safe_read_rows(SESSIONS_TAB)

    # Look up today's session
    today_session_id = f"{user_id}-{today_date}"
    today_session: dict[str, Any] | None = None
    for r in session_rows:
        if r.get("session_id") == today_session_id and int(r.get("user_id", -1)) == user_id:
            today_session = r
            break

    is_completed = bool(today_session and today_session.get("completed_at", ""))

    # Count sets already logged today per exercise
    today_sets_by_exercise: dict[str, int] = {}
    for r in all_set_rows:
        if r.get("session_id") == today_session_id:
            ex = str(r.get("exercise_name", ""))
            today_sets_by_exercise[ex] = today_sets_by_exercise.get(ex, 0) + 1

    exercises: list[TodayExercise] = []
    total_sets = 0
    for r in ex_rows:
        ex_name = str(r["exercise_name"])
        sets = int(r["sets"])
        rep_min = int(r["rep_min"])
        rep_max = int(r["rep_max"])
        last_weight, last_reps = _get_last_set_from_rows(all_set_rows, user_id, ex_name)
        suggestion = compute_suggestion(ex_name, rep_min, rep_max, last_weight, last_reps)
        exercises.append(
            TodayExercise(
                exercise_name=ex_name,
                sets=sets,
                rep_min=rep_min,
                rep_max=rep_max,
                order=int(r.get("order", 0)),
                last_weight_kg=last_weight,
                last_reps=last_reps,
                suggestion=suggestion,
                sets_logged_today=today_sets_by_exercise.get(ex_name, 0),
            )
        )
        total_sets += sets

    estimated_duration_min = math.ceil(total_sets * 2 + 5)

    return TodayWorkoutResponse(
        date=today_date,
        day_name=day_name,
        is_rest_day=False,
        exercises=exercises,
        estimated_duration_min=estimated_duration_min,
        session_id=today_session_id if today_session else None,
        is_completed=is_completed,
        plan_name=plan_name,
    )


def log_set(user_id: int, data: LogSetRequest) -> LogSetResponse:
    now = _now_utc()
    session_id = f"{user_id}-{data.date}"
    active_plan_id = get_active_plan_id(user_id)

    session_rows = _safe_read_rows(SESSIONS_TAB)

    exists = any(r.get("session_id") == session_id for r in session_rows)
    if not exists:
        append_row(
            SESSIONS_TAB,
            {
                "user_id": user_id,
                "plan_id": active_plan_id or "",
                "session_id": session_id,
                "date": data.date,
                "day_name": data.day_name,
                "started_at": now,
                "completed_at": "",
            },
        )
        logger.info("Created session %s", session_id)

    set_rows = _safe_read_rows(SETS_TAB)

    existing = [
        r for r in set_rows
        if r.get("session_id") == session_id
        and r.get("exercise_name") == data.exercise_name
    ]
    set_number = len(existing) + 1

    append_row(
        SETS_TAB,
        {
            "user_id": user_id,
            "session_id": session_id,
            "exercise_name": data.exercise_name,
            "set_number": set_number,
            "weight_kg": data.weight_kg,
            "reps": data.reps,
            "logged_at": now,
        },
    )

    program_rows = _safe_read_rows(PROGRAMS_TAB)
    plan_programs = _filter_by_plan(program_rows, user_id, active_plan_id)
    rep_min, rep_max = _get_program_rep_range_from_rows(plan_programs, user_id, data.exercise_name)
    suggestion = compute_suggestion(data.exercise_name, rep_min, rep_max, data.weight_kg, data.reps)

    logger.info(
        "Logged set: user_id=%s session=%s exercise=%s set=%s %skg×%s",
        user_id, session_id, data.exercise_name, set_number, data.weight_kg, data.reps,
    )

    return LogSetResponse(
        session_id=session_id,
        exercise_name=data.exercise_name,
        set_number=set_number,
        weight_kg=data.weight_kg,
        reps=data.reps,
        logged_at=now,
        suggestion=suggestion,
    )


def complete_session(user_id: int, date_str: str) -> None:
    session_id = f"{user_id}-{date_str}"
    session_rows = _safe_read_rows(SESSIONS_TAB)

    for i, r in enumerate(session_rows):
        if r.get("session_id") == session_id and int(r.get("user_id", -1)) == user_id:
            row_index = i + 2
            updated = dict(r)
            updated["completed_at"] = _now_utc()
            update_row(SESSIONS_TAB, row_index, updated)
            logger.info("Completed session %s", session_id)
            return


def get_progression(user_id: int, exercise_name: str) -> ExerciseProgressionResponse:
    # Read both tabs once — no secondary reads inside helpers
    set_rows = _safe_read_rows(SETS_TAB)
    program_rows = _safe_read_rows(PROGRAMS_TAB)
    active_plan_id = get_active_plan_id(user_id)
    # Rep range is looked up from the active plan; history spans all plans (intended)
    plan_programs = _filter_by_plan(program_rows, user_id, active_plan_id)

    user_rows = [
        r for r in set_rows
        if int(r.get("user_id", -1)) == user_id
        and r.get("exercise_name") == exercise_name
    ]

    # Group by session_id
    sessions: dict[str, list[dict]] = {}
    for r in user_rows:
        sid = str(r.get("session_id", ""))
        sessions.setdefault(sid, []).append(r)

    # Sort sessions by date (extracted from session_id: "{user_id}-{date}")
    def _session_date(sid: str) -> str:
        parts = sid.split("-", 1)
        return parts[1] if len(parts) == 2 else sid

    sorted_sessions = sorted(sessions.keys(), key=_session_date, reverse=True)[:5]

    last_5: list[dict] = []
    for sid in sorted_sessions:
        sets_in_session = sorted(sessions[sid], key=lambda r: int(r.get("set_number", 0)))
        last_5.append(
            {
                "date": _session_date(sid),
                "sets": [
                    {
                        "set_number": int(r["set_number"]),
                        "weight_kg": float(r["weight_kg"]),
                        "reps": int(r["reps"]),
                    }
                    for r in sets_in_session
                ],
            }
        )

    last_weight, last_reps = _get_last_set_from_rows(set_rows, user_id, exercise_name)
    rep_min, rep_max = _get_program_rep_range_from_rows(plan_programs, user_id, exercise_name)
    suggestion = compute_suggestion(exercise_name, rep_min, rep_max, last_weight, last_reps)

    return ExerciseProgressionResponse(
        exercise_name=exercise_name,
        last_5_sessions=last_5,
        suggestion=suggestion,
    )


async def ai_import_workout(
    user_id: int,
    program_name: str,
    raw_text: str,
) -> WorkoutImportResponse:
    """Use AI to parse free-form workout text and import it as a new plan.

    Uses the OpenAI SDK's native structured-output API
    (``beta.chat.completions.parse``) so the response is validated against the
    ``_ParsedWorkout`` Pydantic model before any sheet writes occur.

    The previous plan is kept in the library (not deleted); the new import
    becomes the active plan.
    """
    import os

    from pydantic import BaseModel as _BaseModel

    from ..agent.llm import get_async_client
    from .workout_parser import _auto_schedule

    class _ScheduleEntry(_BaseModel):
        weekday: int  # 0=Mon … 6=Sun
        day_index: int  # 0-based index into the days list

    class _ParsedWorkout(_BaseModel):
        days: list[WorkoutDaySummary]
        schedule: list[_ScheduleEntry] | None = None

    client = get_async_client()

    completion = await client.beta.chat.completions.parse(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        response_format=_ParsedWorkout,
        messages=[
            {
                "role": "system",
                    "content": (
                    "Parse the workout text into structured days and exercises. "
                    "For each training day extract: day_name, exercises with exercise_name, sets, rep_min, rep_max, order. "
                    "Set rep_min = rep_max when only one rep count is given. "
                    "order is 1-based position within the day. "
                    "If weekday assignments are explicit in the text, include a schedule where each entry has "
                    "weekday (0=Mon…6=Sun) and day_index as the 0-based index of that day in the days array. "
                    "IMPORTANT: rest days MUST use day_name='Rest' (exactly, no weekday prefix or suffix). "
                    "Never use names like 'Thursday — Rest', 'Sunday Rest', or 'Rest Day' — only the single word 'Rest'. "
                    "Rest days have day_name='Rest' and an empty exercises list."
                ),
            },
            {"role": "user", "content": raw_text},
        ],
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("Structured output parsing returned no result — model may have refused or run out of tokens.")

    if parsed.schedule:
        schedule = [
            (e.weekday, parsed.days[e.day_index].day_name)
            for e in parsed.schedule
            if 0 <= e.day_index < len(parsed.days)
        ]
        if not schedule:
            schedule = _auto_schedule(parsed.days)
    else:
        schedule = _auto_schedule(parsed.days)

    return await asyncio.to_thread(import_workout, user_id, program_name, parsed.days, schedule)


_WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_schedule(user_id: int) -> WorkoutScheduleResponse:
    active_plan_id = get_active_plan_id(user_id)

    schedule_rows = _safe_read_rows(SCHEDULES_TAB)
    plan_schedule = _filter_by_plan(schedule_rows, user_id, active_plan_id)

    program_rows = _safe_read_rows(PROGRAMS_TAB)
    plan_programs = _filter_by_plan(program_rows, user_id, active_plan_id)

    # Resolve plan name
    plan_name: str | None = None
    if active_plan_id is not None:
        plan_rows = _safe_read_rows(PLANS_TAB)
        for r in plan_rows:
            if int(r.get("user_id", -1)) == user_id and str(r.get("plan_id", "")) == active_plan_id:
                plan_name = str(r.get("plan_name", "")) or None
                break
    else:
        # Legacy fallback: read plan_name from the program_name column
        for r in sorted(plan_programs, key=lambda r: int(r.get("order", 0))):
            candidate = str(r.get("program_name", "")).strip()
            if candidate:
                plan_name = candidate
                break

    # Build weekday → day_name map from stored schedule
    day_name_by_weekday: dict[int, str] = {}
    for r in plan_schedule:
        day_name_by_weekday[int(r["weekday"])] = str(r.get("day_name", "Rest"))

    # Build day_name → exercises map from plan programs
    exercises_by_day: dict[str, list[ExerciseInfo]] = {}
    for r in sorted(plan_programs, key=lambda r: int(r.get("order", 0))):
        if not r.get("exercise_name"):
            continue
        day = str(r.get("day_name", ""))
        exercises_by_day.setdefault(day, []).append(
            ExerciseInfo(
                exercise_name=str(r["exercise_name"]),
                sets=int(r["sets"]),
                rep_min=int(r["rep_min"]),
                rep_max=int(r["rep_max"]),
                order=int(r.get("order", 0)),
            )
        )

    days: list[ScheduleDay] = []
    for weekday in range(7):
        day_name = day_name_by_weekday.get(weekday, "Rest")
        is_rest = day_name == "Rest"
        days.append(
            ScheduleDay(
                weekday=weekday,
                weekday_name=_WEEKDAY_NAMES[weekday],
                day_name=day_name,
                is_rest=is_rest,
                exercises=[] if is_rest else exercises_by_day.get(day_name, []),
            )
        )

    return WorkoutScheduleResponse(program_name=plan_name, days=days)


def get_history(user_id: int) -> WorkoutHistoryResponse:
    session_rows = _safe_read_rows(SESSIONS_TAB)

    user_sessions = [
        {
            "session_id": str(r.get("session_id", "")),
            "date": str(r.get("date", "")),
            "day_name": str(r.get("day_name", "")),
            "started_at": str(r.get("started_at", "")),
            "completed_at": str(r.get("completed_at", "")),
        }
        for r in session_rows
        if int(r.get("user_id", -1)) == user_id
    ]

    user_sessions.sort(key=lambda s: s["date"], reverse=True)
    return WorkoutHistoryResponse(sessions=user_sessions)
