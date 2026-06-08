"""
Unit tests for api/services/workout_parser.py.

All tests call the parser directly — no fixtures or mocking needed.
"""

import os
import sys

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-sheet-id")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

import pytest

from api.services.workout_parser import WorkoutParseError, _auto_schedule, parse_workout_import

# ---------------------------------------------------------------------------
# Plan parsing
# ---------------------------------------------------------------------------

VALID_PPL = """
Push:
Bench Press 3x8-12
Overhead Press 3x8-10
Tricep Pushdown 3x12-15

Pull:
Barbell Row 3x8-12
Lat Pulldown 3x10-12

Legs:
Squat 3x6-10
Romanian Deadlift 3x8-12

Rest
Rest
"""

VALID_SCHEDULE = """
Mon - Push
Tue - Pull
Wed - Legs
Thu - Rest
Fri - Push
Sat - Pull
Sun - Rest
"""


def test_valid_ppl_plan_parses_day_count():
    days, _ = parse_workout_import(VALID_PPL, VALID_SCHEDULE)
    day_names = [d.day_name for d in days]
    assert "Push" in day_names
    assert "Pull" in day_names
    assert "Legs" in day_names
    assert day_names.count("Rest") == 2


def test_valid_ppl_plan_exercise_counts():
    days, _ = parse_workout_import(VALID_PPL, VALID_SCHEDULE)
    push = next(d for d in days if d.day_name == "Push")
    assert len(push.exercises) == 3
    pull = next(d for d in days if d.day_name == "Pull")
    assert len(pull.exercises) == 2


def test_exercise_order_values():
    days, _ = parse_workout_import(VALID_PPL, VALID_SCHEDULE)
    push = next(d for d in days if d.day_name == "Push")
    orders = [e.order for e in push.exercises]
    assert orders == [1, 2, 3]


def test_exercise_with_rep_range():
    days, _ = parse_workout_import(VALID_PPL, VALID_SCHEDULE)
    push = next(d for d in days if d.day_name == "Push")
    bench = next(e for e in push.exercises if e.exercise_name == "Bench Press")
    assert bench.sets == 3
    assert bench.rep_min == 8
    assert bench.rep_max == 12


def test_exercise_without_rep_range():
    plan = "Push:\nSquat 5x5\n"
    days, _ = parse_workout_import(plan, "")
    squat = days[0].exercises[0]
    assert squat.rep_min == 5
    assert squat.rep_max == 5


def test_rest_day_produces_empty_exercises():
    plan = "Push:\nBench Press 3x8-12\nRest\n"
    days, _ = parse_workout_import(plan, "")
    rest_day = next(d for d in days if d.day_name == "Rest")
    assert rest_day.exercises == []


def test_blank_lines_between_blocks_ignored():
    plan = "\nPush:\n\nBench Press 3x8-12\n\nRest\n"
    days, _ = parse_workout_import(plan, "")
    assert len(days) == 2


def test_invalid_exercise_line_raises_with_line_number():
    plan = "Push:\nBench Press 3x8-12\nthis is not valid\n"
    with pytest.raises(WorkoutParseError) as exc_info:
        parse_workout_import(plan, "")
    assert exc_info.value.line_number == 3


def test_exercise_before_header_raises():
    plan = "Bench Press 3x8-12\nPush:\n"
    with pytest.raises(WorkoutParseError):
        parse_workout_import(plan, "")


def test_header_with_slash_parsed():
    plan = "Upper/Lower:\nBench Press 3x8-12\n"
    days, _ = parse_workout_import(plan, "")
    assert days[0].day_name == "Upper/Lower"


# ---------------------------------------------------------------------------
# Schedule parsing
# ---------------------------------------------------------------------------


def test_valid_schedule_text_produces_correct_tuples():
    _, schedule = parse_workout_import(VALID_PPL, VALID_SCHEDULE)
    mapping = dict(schedule)
    assert mapping[0] == "Push"   # Mon
    assert mapping[1] == "Pull"   # Tue
    assert mapping[2] == "Legs"   # Wed
    assert mapping[3] == "Rest"   # Thu


def test_schedule_case_insensitive():
    plan = "Push:\nBench Press 3x8\n"
    schedule_text = "mon - Push\nTUE - Rest\n"
    _, schedule = parse_workout_import(plan, schedule_text)
    mapping = dict(schedule)
    assert mapping[0] == "Push"
    assert mapping[1] == "Rest"


def test_empty_schedule_auto_assigns_from_plan():
    plan = "Push:\nBench Press 3x8-12\nPull:\nRow 3x8-12\nRest\n"
    days, schedule = parse_workout_import(plan, "")
    assert len(schedule) == 7
    mapping = dict(schedule)
    assert mapping[0] == "Push"   # Mon
    assert mapping[1] == "Pull"   # Tue
    # Remaining days should be Rest
    assert all(mapping[i] == "Rest" for i in range(2, 7))


def test_invalid_schedule_line_raises():
    plan = "Push:\nBench Press 3x8\n"
    bad_schedule = "Monday - Push\n"  # "Monday" is not a valid abbreviation
    with pytest.raises(WorkoutParseError):
        parse_workout_import(plan, bad_schedule)


def test_rest_line_case_insensitive():
    plan = "Push:\nBench Press 3x8\nREST\n"
    with pytest.raises(WorkoutParseError):
        # "REST" (all caps) should NOT match — only "Rest" or "rest" per spec
        parse_workout_import(plan, "")


# ---------------------------------------------------------------------------
# _auto_schedule: rest-like name handling (regression tests)
# ---------------------------------------------------------------------------


def _day(name: str, has_exercises: bool = True):
    from api.models.workout import ExerciseInfo, WorkoutDaySummary
    exercises = [ExerciseInfo(exercise_name="Ex", sets=3, rep_min=8, rep_max=12, order=1)] if has_exercises else []
    return WorkoutDaySummary(day_name=name, exercises=exercises)


def test_auto_schedule_treats_verbose_rest_as_rest():
    """'Thursday — Rest' must not occupy a weekday slot."""
    days = [
        _day("Legs"),
        _day("Push"),
        _day("Thursday — Rest", has_exercises=False),
    ]
    result = dict(_auto_schedule(days))
    assert result[0] == "Legs"
    assert result[1] == "Push"
    # "Thursday — Rest" is rest-like → not assigned to a slot
    assert "Thursday — Rest" not in result.values()
    assert all(result[i] == "Rest" for i in range(2, 7))


def test_auto_schedule_treats_rest_day_as_rest():
    """'Rest Day' (with suffix) must also be treated as rest."""
    days = [
        _day("Pull"),
        _day("Rest Day", has_exercises=False),
    ]
    result = dict(_auto_schedule(days))
    assert result[0] == "Pull"
    assert "Rest Day" not in result.values()
    assert all(result[i] == "Rest" for i in range(1, 7))


def test_auto_schedule_treats_sunday_rest_as_rest():
    """'Sunday — Rest' produced by AI should be treated as rest."""
    days = [
        _day("Upper"),
        _day("Lower"),
        _day("Sunday — Rest", has_exercises=False),
    ]
    result = dict(_auto_schedule(days))
    non_rest = [v for v in result.values() if v != "Rest"]
    assert set(non_rest) == {"Upper", "Lower"}
    assert "Sunday — Rest" not in result.values()
