"""
Workout service — business logic for Phase 3.

Tabs used:
    WorkoutPrograms  — one row per exercise per workout day
    WorkoutSchedules — one row per weekday (0=Mon … 6=Sun)
    WorkoutSessions  — one row per session (auto-created on first set log)
    WorkoutSets      — one row per set logged
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
    WorkoutScheduleResponse,
)
from ..sheets.sheets_client import get_worksheet
from ..sheets.sheets_repo import append_row, append_rows_batch, read_rows, update_row

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


def _get_last_set_from_rows(
    set_rows: list[dict[str, Any]],
    user_id: int,
    exercise_name: str,
) -> tuple[float | None, int | None]:
    """
    Return (weight_kg, reps) from the final set of the most recent session.

    Operates on a pre-loaded list of rows — no additional Sheets I/O.
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
    """
    for r in program_rows:
        if (
            int(r.get("user_id", -1)) == user_id
            and r.get("exercise_name", "") == exercise_name
        ):
            return int(r["rep_min"]), int(r["rep_max"])
    return 8, 12


def _get_program_rep_range(user_id: int, exercise_name: str) -> tuple[int, int]:
    """Look up rep_min/rep_max from WorkoutPrograms; fall back to (8, 12)."""
    return _get_program_rep_range_from_rows(
        _safe_read_rows(PROGRAMS_TAB), user_id, exercise_name
    )


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

    # Replace all existing program + schedule rows for this user
    _delete_user_rows(PROGRAMS_TAB, user_id)
    _delete_user_rows(SCHEDULES_TAB, user_id)

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
                "weekday": weekday,
                "day_name": day_name,
                "created_at": now,
            }
        )

    append_rows_batch(PROGRAMS_TAB, program_rows)
    append_rows_batch(SCHEDULES_TAB, schedule_rows)

    rest_days = sum(1 for d in days if d.day_name == "Rest")
    logger.info("Imported workout for user_id=%s: %s days, %s exercises", user_id, program_days, total_exercises)

    return WorkoutImportResponse(
        program_name=program_name,
        program_days=program_days,
        rest_days=rest_days,
        total_exercises=total_exercises,
        days=days,
    )


def get_today_workout(user_id: int, today_date: str) -> TodayWorkoutResponse:
    weekday = date.fromisoformat(today_date).weekday()  # 0=Mon

    schedule_rows = _safe_read_rows(SCHEDULES_TAB)

    day_name: str | None = None
    for r in schedule_rows:
        if int(r.get("user_id", -1)) == user_id and int(r.get("weekday", -1)) == weekday:
            day_name = str(r.get("day_name", "")) or None
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
        )

    program_rows = _safe_read_rows(PROGRAMS_TAB)

    ex_rows = sorted(
        [
            r for r in program_rows
            if int(r.get("user_id", -1)) == user_id
            and r.get("day_name") == day_name
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
    )


def log_set(user_id: int, data: LogSetRequest) -> LogSetResponse:
    now = _now_utc()
    session_id = f"{user_id}-{data.date}"

    session_rows = _safe_read_rows(SESSIONS_TAB)

    exists = any(r.get("session_id") == session_id for r in session_rows)
    if not exists:
        append_row(
            SESSIONS_TAB,
            {
                "user_id": user_id,
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

    rep_min, rep_max = _get_program_rep_range(user_id, data.exercise_name)
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

    # Reuse already-loaded rows — no extra Sheets calls
    last_weight, last_reps = _get_last_set_from_rows(set_rows, user_id, exercise_name)
    rep_min, rep_max = _get_program_rep_range_from_rows(program_rows, user_id, exercise_name)
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
    """Use AI to parse free-form workout text and import it.

    Uses the OpenAI SDK's native structured-output API
    (``beta.chat.completions.parse``) so the response is validated against the
    ``_ParsedWorkout`` Pydantic model before any sheet writes occur.
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
                    "Rest days have day_name='Rest' and empty exercises list."
                ),
            },
            {"role": "user", "content": raw_text},
        ],
    )

    parsed = completion.choices[0].message.parsed
    if parsed is None:
        raise ValueError("Structured output parsing returned no result — model may have refused or run out of tokens.")

    schedule = (
        [
            (e.weekday, parsed.days[e.day_index].day_name)
            for e in parsed.schedule
            if 0 <= e.day_index < len(parsed.days)
        ]
        if parsed.schedule
        else _auto_schedule(parsed.days)
    )

    return await asyncio.to_thread(import_workout, user_id, program_name, parsed.days, schedule)


_WEEKDAY_NAMES = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def get_schedule(user_id: int) -> WorkoutScheduleResponse:
    schedule_rows = _safe_read_rows(SCHEDULES_TAB)
    program_rows = _safe_read_rows(PROGRAMS_TAB)

    # Build weekday → day_name map from stored schedule
    day_name_by_weekday: dict[int, str] = {}
    for r in schedule_rows:
        if int(r.get("user_id", -1)) == user_id:
            day_name_by_weekday[int(r["weekday"])] = str(r.get("day_name", "Rest"))

    # Build day_name → exercises map from program
    exercises_by_day: dict[str, list[ExerciseInfo]] = {}
    program_name: str | None = None
    for r in sorted(program_rows, key=lambda r: int(r.get("order", 0))):
        if int(r.get("user_id", -1)) != user_id:
            continue
        if program_name is None:
            program_name = str(r.get("program_name", "")) or None
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

    return WorkoutScheduleResponse(program_name=program_name, days=days)


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
