"""
Workout service — business logic for Phase 3.

Tabs used:
    WorkoutPrograms  — one row per exercise per workout day
    WorkoutSchedules — one row per weekday (0=Mon … 6=Sun)
    WorkoutSessions  — one row per session (auto-created on first set log)
    WorkoutSets      — one row per set logged
"""

from __future__ import annotations

import math
import os
from datetime import date, datetime, timezone

import gspread.exceptions
from openai import AsyncAzureOpenAI

from ..agent.prompts import WORKOUT_IMPORT_PROMPT
from ..logger import get_logger
from ..models.workout import (
    ExerciseInfo,
    ExerciseProgressionResponse,
    LogSetRequest,
    LogSetResponse,
    ProgressionSuggestion,
    TodayExercise,
    TodayWorkoutResponse,
    WorkoutDaySummary,
    WorkoutHistoryResponse,
    WorkoutImportResponse,
)
from .workout_parser import parse_workout_import
from ..sheets.sheets_client import get_main_sheet
from ..sheets.sheets_repo import append_row, read_rows, update_row

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


def _delete_user_rows(tab: str, user_id: int) -> None:
    """Delete all rows belonging to user_id in the given tab."""
    try:
        ws = get_main_sheet().worksheet(tab)
    except gspread.exceptions.WorksheetNotFound:
        return
    records = ws.get_all_records()
    indices = [
        i + 2  # +1 for header row, +1 for 0-based → 1-based
        for i, r in enumerate(records)
        if int(r.get("user_id", -1)) == user_id
    ]
    for row_idx in reversed(indices):
        ws.delete_rows(row_idx)


def _get_last_set(user_id: int, exercise_name: str) -> tuple[float | None, int | None]:
    """Return (weight_kg, reps) from the final set of the most recent session."""
    try:
        rows = read_rows(SETS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return None, None

    user_rows = [
        r for r in rows
        if int(r.get("user_id", -1)) == user_id
        and r.get("exercise_name", "") == exercise_name
    ]
    if not user_rows:
        return None, None

    # Sort by logged_at descending to find the most recent session
    user_rows.sort(key=lambda r: r.get("logged_at", ""), reverse=True)
    most_recent_session = user_rows[0].get("session_id", "")

    session_rows = [r for r in user_rows if r.get("session_id") == most_recent_session]
    # Pick the set with the highest set_number within that session
    last_row = max(session_rows, key=lambda r: int(r.get("set_number", 0)))
    return float(last_row["weight_kg"]), int(last_row["reps"])


def _get_program_rep_range(user_id: int, exercise_name: str) -> tuple[int, int]:
    """Look up rep_min/rep_max from WorkoutPrograms; fall back to (8, 12)."""
    try:
        rows = read_rows(PROGRAMS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return 8, 12

    for r in rows:
        if (
            int(r.get("user_id", -1)) == user_id
            and r.get("exercise_name", "") == exercise_name
        ):
            return int(r["rep_min"]), int(r["rep_max"])
    return 8, 12


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

    for day in days:
        if day.day_name == "Rest":
            continue
        program_days += 1
        for ex in day.exercises:
            append_row(
                PROGRAMS_TAB,
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
                },
            )
            total_exercises += 1

    for weekday, day_name in schedule:
        append_row(
            SCHEDULES_TAB,
            {
                "user_id": user_id,
                "weekday": weekday,
                "day_name": day_name,
                "created_at": now,
            },
        )

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

    # Look up today's day_name from schedule
    try:
        schedule_rows = read_rows(SCHEDULES_TAB)
    except gspread.exceptions.WorksheetNotFound:
        schedule_rows = []

    day_name: str | None = None
    for r in schedule_rows:
        if int(r.get("user_id", -1)) == user_id and int(r.get("weekday", -1)) == weekday:
            day_name = str(r["day_name"])
            break

    if day_name is None or day_name == "Rest":
        return TodayWorkoutResponse(
            date=today_date,
            day_name=day_name or "Rest",
            is_rest_day=True,
            exercises=[],
            estimated_duration_min=0,
        )

    # Load exercises for this day_name
    try:
        program_rows = read_rows(PROGRAMS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        program_rows = []

    ex_rows = sorted(
        [
            r for r in program_rows
            if int(r.get("user_id", -1)) == user_id and r.get("day_name") == day_name
        ],
        key=lambda r: int(r.get("order", 0)),
    )

    exercises: list[TodayExercise] = []
    total_sets = 0
    for r in ex_rows:
        ex_name = str(r["exercise_name"])
        sets = int(r["sets"])
        rep_min = int(r["rep_min"])
        rep_max = int(r["rep_max"])
        last_weight, last_reps = _get_last_set(user_id, ex_name)
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
    )


def log_set(user_id: int, data: LogSetRequest) -> LogSetResponse:
    now = _now_utc()
    session_id = f"{user_id}-{data.date}"

    # Auto-create session row if it doesn't exist yet
    try:
        session_rows = read_rows(SESSIONS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        session_rows = []

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

    # Count existing sets for this exercise in this session
    try:
        set_rows = read_rows(SETS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        set_rows = []

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
    try:
        session_rows = read_rows(SESSIONS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return

    for i, r in enumerate(session_rows):
        if r.get("session_id") == session_id and int(r.get("user_id", -1)) == user_id:
            row_index = i + 2
            updated = dict(r)
            updated["completed_at"] = _now_utc()
            update_row(SESSIONS_TAB, row_index, updated)
            logger.info("Completed session %s", session_id)
            return


def get_progression(user_id: int, exercise_name: str) -> ExerciseProgressionResponse:
    try:
        set_rows = read_rows(SETS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        set_rows = []

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

    # Suggestion based on the most recent session's last set
    last_weight, last_reps = _get_last_set(user_id, exercise_name)
    rep_min, rep_max = _get_program_rep_range(user_id, exercise_name)
    suggestion = compute_suggestion(exercise_name, rep_min, rep_max, last_weight, last_reps)

    return ExerciseProgressionResponse(
        exercise_name=exercise_name,
        last_5_sessions=last_5,
        suggestion=suggestion,
    )


def get_history(user_id: int) -> WorkoutHistoryResponse:
    try:
        session_rows = read_rows(SESSIONS_TAB)
    except gspread.exceptions.WorksheetNotFound:
        session_rows = []

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


async def ai_import_workout(user_id: int, program_name: str, raw_text: str) -> WorkoutImportResponse:
    client = AsyncAzureOpenAI(
        api_key=os.environ["AZURE_OPENAI_API_KEY"],
        azure_endpoint=os.environ["AZURE_OPENAI_ENDPOINT"],
        api_version="2024-08-01-preview",
    )
    deployment = os.environ["AZURE_OPENAI_DEPLOYMENT"]
    response = await client.chat.completions.create(
        model=deployment,
        messages=[
            {"role": "system", "content": WORKOUT_IMPORT_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        temperature=0.1,
    )
    converted_text = response.choices[0].message.content.strip()
    logger.info("AI-converted workout plan for user %s:\n%s", user_id, converted_text)
    days, schedule = parse_workout_import(converted_text, schedule_text="")
    return import_workout(user_id, program_name, days, schedule)
