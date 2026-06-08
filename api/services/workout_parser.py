"""
Workout plan text parser.

Public API
----------
parse_workout_import(plan_text, schedule_text)
    -> (list[WorkoutDaySummary], list[tuple[int, str]])

Raises WorkoutParseError on invalid input.
"""

from __future__ import annotations

import re

from ..models.workout import ExerciseInfo, WorkoutDaySummary

# ---------------------------------------------------------------------------
# Error type
# ---------------------------------------------------------------------------

_WEEKDAY_MAP: dict[str, int] = {
    "mon": 0, "tue": 1, "wed": 2, "thu": 3,
    "fri": 4, "sat": 5, "sun": 6,
}

_HEADER_RE = re.compile(r"^([A-Za-z /]+):\s*$")
_EXERCISE_RE = re.compile(r"^(.+?)\s+(\d+)x(\d+)(?:-(\d+))?\s*$")
_REST_RE = re.compile(r"^[Rr]est\s*$")
_SCHEDULE_RE = re.compile(r"^(Mon|Tue|Wed|Thu|Fri|Sat|Sun)\s*[-–]\s*(.+)$", re.IGNORECASE)


class WorkoutParseError(Exception):
    def __init__(self, message: str, line_number: int | None = None) -> None:
        self.line_number = line_number
        detail = f"line {line_number}: {message}" if line_number is not None else message
        super().__init__(detail)


# ---------------------------------------------------------------------------
# Plan parser
# ---------------------------------------------------------------------------


def _parse_plan(plan_text: str) -> list[WorkoutDaySummary]:
    days: list[WorkoutDaySummary] = []
    current_day: str | None = None
    current_exercises: list[ExerciseInfo] = []
    current_order = 0

    def _flush() -> None:
        nonlocal current_day, current_exercises, current_order
        if current_day is not None:
            days.append(WorkoutDaySummary(day_name=current_day, exercises=current_exercises))
            current_day = None
            current_exercises = []
            current_order = 0

    for lineno, raw in enumerate(plan_text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue

        if _REST_RE.match(line):
            _flush()
            days.append(WorkoutDaySummary(day_name="Rest", exercises=[]))
            continue

        m_header = _HEADER_RE.match(line)
        if m_header:
            _flush()
            current_day = m_header.group(1).strip()
            continue

        m_exercise = _EXERCISE_RE.match(line)
        if m_exercise:
            if current_day is None:
                raise WorkoutParseError("exercise line found before any day header", lineno)
            name = m_exercise.group(1).strip()
            sets = int(m_exercise.group(2))
            rep_a = int(m_exercise.group(3))
            rep_b = int(m_exercise.group(4)) if m_exercise.group(4) else rep_a
            current_order += 1
            current_exercises.append(
                ExerciseInfo(
                    exercise_name=name,
                    sets=sets,
                    rep_min=rep_a,
                    rep_max=rep_b,
                    order=current_order,
                )
            )
            continue

        raise WorkoutParseError(f"unrecognised line: '{line}'", lineno)

    _flush()
    return days


# ---------------------------------------------------------------------------
# Schedule parser
# ---------------------------------------------------------------------------


def _parse_schedule(schedule_text: str) -> list[tuple[int, str]]:
    entries: list[tuple[int, str]] = []
    for lineno, raw in enumerate(schedule_text.splitlines(), start=1):
        line = raw.strip()
        if not line:
            continue
        m = _SCHEDULE_RE.match(line)
        if not m:
            raise WorkoutParseError(f"unrecognised schedule line: '{line}'", lineno)
        weekday = _WEEKDAY_MAP[m.group(1).lower()]
        day_name = m.group(2).strip()
        entries.append((weekday, day_name))
    return entries


def _auto_schedule(days: list[WorkoutDaySummary]) -> list[tuple[int, str]]:
    """Cycle non-rest days over Mon–Sun; remaining slots get 'Rest'."""
    non_rest = [d.day_name for d in days if "rest" not in d.day_name.lower()]
    result: list[tuple[int, str]] = []
    cycle_idx = 0
    for weekday in range(7):
        if cycle_idx < len(non_rest):
            result.append((weekday, non_rest[cycle_idx]))
            cycle_idx += 1
        else:
            result.append((weekday, "Rest"))
    return result


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse_workout_import(
    plan_text: str,
    schedule_text: str,
) -> tuple[list[WorkoutDaySummary], list[tuple[int, str]]]:
    """
    Parse workout plan text and optional schedule text.

    Returns:
        (days, schedule) where schedule is a list of (weekday_int, day_name) tuples.
        weekday_int: 0=Monday … 6=Sunday.

    Raises:
        WorkoutParseError: on any malformed input line.
    """
    days = _parse_plan(plan_text)
    if schedule_text.strip():
        schedule = _parse_schedule(schedule_text)
    else:
        schedule = _auto_schedule(days)
    return days, schedule
