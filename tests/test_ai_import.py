"""
Tests for ai_import_workout in api/services/workout_service.py.

The Azure OpenAI call (client.beta.chat.completions.parse) and all sheet
operations are fully mocked — no network traffic and no writes to Google Sheets.

Mocking surface
---------------
- ``api.agent.llm.get_async_client`` is patched to return a mock whose
  ``beta.chat.completions.parse`` is an AsyncMock returning a fake completion.
- ``api.services.workout_service.append_row`` is patched to a MagicMock so no
  actual Sheets writes occur.
- ``api.services.workout_service._delete_user_rows`` is patched to a no-op.

Covered scenarios
-----------------
Schedule derivation
  - auto_schedule used when AI returns no explicit schedule
  - explicit schedule: day_index correctly maps to day_name from days list
  - explicit schedule: out-of-bounds day_index entries are silently skipped
  - explicit schedule: day_index pointing to a Rest day produces "Rest" in schedule
  - explicit schedule: non-sequential indices map to correct day_names
  - partial schedule: only some weekdays provided (rest auto-filled is not expected)

Response fidelity
  - program_days / rest_days / total_exercises counts are correct
  - exercise fields (sets, rep_min, rep_max, order) reach the response unchanged
  - multi-exercise day preserves all exercises in order

Edge cases
  - rest-only program: program_days=0, total_exercises=0
  - single training day program
  - empty schedule list (treated as falsy → auto_schedule)

Sheet write verification
  - append_row called with day_name values that match between Programs and Schedules
  - no append_row calls when LLM raises before import
  - _delete_user_rows called before any append_row on successful import

Structured-output failure
  - parsed=None → ValueError, no sheet writes
  - LLM raises ValueError → propagated, no sheet writes
"""

import os
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, call, patch

import pytest

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-sheet-id")
os.environ.setdefault("GOOGLE_CHAT_HISTORY_SHEET_ID", "test-chat-history-id")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

from api.models.workout import ExerciseInfo, WorkoutDaySummary
from api.services.workout_service import ai_import_workout


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ex(name: str, *, sets: int = 3, rep_min: int = 8, rep_max: int = 12, order: int = 1) -> ExerciseInfo:
    return ExerciseInfo(exercise_name=name, sets=sets, rep_min=rep_min, rep_max=rep_max, order=order)


def _parsed(days: list[WorkoutDaySummary], schedule=None):
    """Duck-typed stand-in for the locally-defined _ParsedWorkout model."""
    return SimpleNamespace(days=days, schedule=schedule)


def _sched(*entries):
    """Build a list of SimpleNamespace schedule entries from (weekday, day_index) tuples."""
    return [SimpleNamespace(weekday=wd, day_index=di) for wd, di in entries]


def _ai_mocks(parsed_return, mock_append=None, mock_delete=None):
    """
    Return an ExitStack that wires up all mocks needed by ai_import_workout:

      - get_async_client() → mock client with beta.chat.completions.parse as AsyncMock
      - append_row → no-op (or supplied mock) so no Sheets writes happen
      - _delete_user_rows → no-op (or supplied mock)
    """
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.parsed = parsed_return
    mock_client.beta.chat.completions.parse = AsyncMock(return_value=mock_completion)

    stack = ExitStack()
    stack.enter_context(patch("api.agent.llm.get_async_client", return_value=mock_client))
    stack.enter_context(
        patch("api.services.workout_service.append_row", mock_append or MagicMock())
    )
    stack.enter_context(
        patch("api.services.workout_service._delete_user_rows", mock_delete or MagicMock())
    )
    return stack


# ---------------------------------------------------------------------------
# Schedule derivation
# ---------------------------------------------------------------------------


async def test_auto_schedule_used_when_no_explicit_schedule():
    """When AI returns schedule=None, _auto_schedule cycles days from Monday."""
    days = [
        WorkoutDaySummary(day_name="Push", exercises=[_ex("Bench Press")]),
        WorkoutDaySummary(day_name="Pull", exercises=[_ex("Barbell Row")]),
        WorkoutDaySummary(day_name="Legs", exercises=[_ex("Squat")]),
    ]

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days, schedule=None), mock_append=mock_append):
        result = await ai_import_workout(user_id=1, program_name="PPL", raw_text="...")

    assert result.program_days == 3
    assert result.total_exercises == 3

    # WorkoutSchedules rows: weekday 0=Push, 1=Pull, 2=Legs, 3-6=Rest
    sched_calls = [
        c for c in mock_append.call_args_list if c.args[0] == "WorkoutSchedules"
    ]
    assert len(sched_calls) == 7
    assert sched_calls[0].args[1]["weekday"] == 0
    assert sched_calls[0].args[1]["day_name"] == "Push"
    assert sched_calls[1].args[1]["day_name"] == "Pull"
    assert sched_calls[2].args[1]["day_name"] == "Legs"
    for sched_call in sched_calls[3:]:
        assert sched_call.args[1]["day_name"] == "Rest"


async def test_explicit_schedule_day_index_maps_to_correct_day_name():
    """day_index in schedule entries is resolved to day_name from the days list."""
    days = [
        WorkoutDaySummary(day_name="Upper", exercises=[_ex("Pull-up")]),
        WorkoutDaySummary(day_name="Lower", exercises=[_ex("Squat")]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
    ]
    # Explicitly: Mon→Upper(0), Tue→Lower(1), Wed→Rest(2)
    schedule = _sched((0, 0), (1, 1), (2, 2))

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days, schedule=schedule), mock_append=mock_append):
        result = await ai_import_workout(user_id=1, program_name="UL", raw_text="...")

    assert result.program_days == 2

    sched_calls = [
        c for c in mock_append.call_args_list if c.args[0] == "WorkoutSchedules"
    ]
    assert len(sched_calls) == 3
    assert sched_calls[0].args[1] == {"user_id": 1, "weekday": 0, "day_name": "Upper", **{"created_at": sched_calls[0].args[1]["created_at"]}}
    assert sched_calls[1].args[1]["day_name"] == "Lower"
    assert sched_calls[2].args[1]["day_name"] == "Rest"


async def test_explicit_schedule_day_name_matches_program_day_name():
    """
    Critical: day_name written to WorkoutSchedules must exactly match the
    day_name written to WorkoutPrograms so get_today_workout can find exercises.
    """
    days = [
        WorkoutDaySummary(day_name="Push", exercises=[_ex("OHP"), _ex("Bench Press", order=2)]),
        WorkoutDaySummary(day_name="Pull", exercises=[_ex("Row")]),
    ]
    schedule = _sched((0, 0), (1, 1))  # Mon→Push, Tue→Pull

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days, schedule=schedule), mock_append=mock_append):
        await ai_import_workout(user_id=1, program_name="PPL", raw_text="...")

    program_day_names = {
        c.args[1]["day_name"]
        for c in mock_append.call_args_list
        if c.args[0] == "WorkoutPrograms"
    }
    schedule_day_names = {
        c.args[1]["day_name"]
        for c in mock_append.call_args_list
        if c.args[0] == "WorkoutSchedules"
    }

    # Every day_name in the schedule must appear in the program
    assert program_day_names == {"Push", "Pull"}
    assert program_day_names == schedule_day_names


async def test_out_of_bounds_day_index_is_skipped():
    """day_index values outside [0, len(days)) are silently dropped."""
    days = [
        WorkoutDaySummary(day_name="Full Body", exercises=[_ex("Deadlift")]),
    ]
    # day_index=0 is valid; day_index=5 and day_index=-1 are out of bounds
    schedule = _sched((0, 0), (3, 5), (6, -1))

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days, schedule=schedule), mock_append=mock_append):
        await ai_import_workout(user_id=1, program_name="Minimal", raw_text="...")

    sched_calls = [
        c for c in mock_append.call_args_list if c.args[0] == "WorkoutSchedules"
    ]
    # Only the valid entry (day_index=0) survives
    assert len(sched_calls) == 1
    assert sched_calls[0].args[1]["weekday"] == 0
    assert sched_calls[0].args[1]["day_name"] == "Full Body"


async def test_day_index_pointing_to_rest_day_produces_rest_in_schedule():
    """If the AI schedules a weekday at a Rest day index, 'Rest' is written correctly."""
    days = [
        WorkoutDaySummary(day_name="Push", exercises=[_ex("Bench")]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
    ]
    schedule = _sched((0, 0), (1, 1))  # Mon→Push(0), Tue→Rest(1)

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days, schedule=schedule), mock_append=mock_append):
        await ai_import_workout(user_id=1, program_name="P", raw_text="...")

    sched_calls = [
        c for c in mock_append.call_args_list if c.args[0] == "WorkoutSchedules"
    ]
    assert sched_calls[1].args[1]["day_name"] == "Rest"


async def test_non_sequential_day_indices_map_correctly():
    """Indices don't need to match position — index 2 maps to the 3rd day."""
    days = [
        WorkoutDaySummary(day_name="A", exercises=[_ex("Ex1")]),
        WorkoutDaySummary(day_name="B", exercises=[_ex("Ex2")]),
        WorkoutDaySummary(day_name="C", exercises=[_ex("Ex3")]),
    ]
    # Use non-sequential mapping: Mon→C(2), Tue→A(0), Wed→B(1)
    schedule = _sched((0, 2), (1, 0), (2, 1))

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days, schedule=schedule), mock_append=mock_append):
        await ai_import_workout(user_id=1, program_name="X", raw_text="...")

    sched_calls = [
        c for c in mock_append.call_args_list if c.args[0] == "WorkoutSchedules"
    ]
    assert sched_calls[0].args[1]["day_name"] == "C"
    assert sched_calls[1].args[1]["day_name"] == "A"
    assert sched_calls[2].args[1]["day_name"] == "B"


async def test_empty_schedule_list_falls_back_to_auto_schedule():
    """schedule=[] is falsy, so _auto_schedule is used."""
    days = [
        WorkoutDaySummary(day_name="Push", exercises=[_ex("Bench")]),
    ]

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days, schedule=[]), mock_append=mock_append):
        await ai_import_workout(user_id=1, program_name="P", raw_text="...")

    sched_calls = [
        c for c in mock_append.call_args_list if c.args[0] == "WorkoutSchedules"
    ]
    # _auto_schedule produces 7 entries (Mon=Push, Tue-Sun=Rest)
    assert len(sched_calls) == 7
    assert sched_calls[0].args[1]["day_name"] == "Push"


# ---------------------------------------------------------------------------
# Response fidelity
# ---------------------------------------------------------------------------


async def test_response_counts_ppl_program():
    """3 training + 2 rest days → correct program_days, rest_days, total_exercises."""
    days = [
        WorkoutDaySummary(day_name="Push", exercises=[_ex("Bench"), _ex("OHP", order=2)]),
        WorkoutDaySummary(day_name="Pull", exercises=[_ex("Row")]),
        WorkoutDaySummary(day_name="Legs", exercises=[_ex("Squat")]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
    ]

    with _ai_mocks(_parsed(days)):
        result = await ai_import_workout(user_id=1, program_name="PPL", raw_text="...")

    assert result.program_name == "PPL"
    assert result.program_days == 3
    assert result.rest_days == 2
    assert result.total_exercises == 4


async def test_exercise_fields_reach_response_unchanged():
    """sets, rep_min, rep_max, order survive the full pipeline unchanged."""
    days = [
        WorkoutDaySummary(day_name="Strength", exercises=[
            _ex("Deadlift", sets=5, rep_min=3, rep_max=5, order=1),
            _ex("Squat",    sets=4, rep_min=4, rep_max=6, order=2),
        ]),
    ]

    with _ai_mocks(_parsed(days)):
        result = await ai_import_workout(user_id=1, program_name="S", raw_text="...")

    exs = result.days[0].exercises
    assert exs[0].exercise_name == "Deadlift"
    assert exs[0].sets == 5
    assert exs[0].rep_min == 3
    assert exs[0].rep_max == 5
    assert exs[0].order == 1
    assert exs[1].exercise_name == "Squat"
    assert exs[1].order == 2


async def test_multi_exercise_day_all_exercises_written_to_programs():
    """Every exercise in a day generates its own append_row to WorkoutPrograms."""
    exercises = [_ex(f"Ex{i}", order=i) for i in range(1, 6)]
    days = [WorkoutDaySummary(day_name="Full Body", exercises=exercises)]

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days), mock_append=mock_append):
        result = await ai_import_workout(user_id=1, program_name="FB", raw_text="...")

    program_calls = [c for c in mock_append.call_args_list if c.args[0] == "WorkoutPrograms"]
    assert len(program_calls) == 5
    assert result.total_exercises == 5
    names = [c.args[1]["exercise_name"] for c in program_calls]
    assert names == ["Ex1", "Ex2", "Ex3", "Ex4", "Ex5"]


# ---------------------------------------------------------------------------
# Edge cases
# ---------------------------------------------------------------------------


async def test_rest_only_program():
    """All 7 days are Rest → program_days=0, total_exercises=0."""
    days = [WorkoutDaySummary(day_name="Rest", exercises=[])] * 7

    with _ai_mocks(_parsed(days)):
        result = await ai_import_workout(user_id=2, program_name="Deload", raw_text="Rest week")

    assert result.program_days == 0
    assert result.total_exercises == 0
    assert result.rest_days == 7


async def test_single_training_day_program():
    """One training day + rest → program_days=1."""
    days = [
        WorkoutDaySummary(day_name="Full Body", exercises=[_ex("Squat"), _ex("Press", order=2)]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
    ]

    with _ai_mocks(_parsed(days)):
        result = await ai_import_workout(user_id=1, program_name="Minimal", raw_text="...")

    assert result.program_days == 1
    assert result.rest_days == 1
    assert result.total_exercises == 2


# ---------------------------------------------------------------------------
# Sheet write verification
# ---------------------------------------------------------------------------


async def test_delete_called_before_append():
    """_delete_user_rows must fire before any append_row so stale data is cleared."""
    days = [WorkoutDaySummary(day_name="Push", exercises=[_ex("Bench")])]
    call_order: list[str] = []

    mock_delete = MagicMock(side_effect=lambda *_: call_order.append("delete"))
    mock_append = MagicMock(side_effect=lambda *_: call_order.append("append"))

    with _ai_mocks(_parsed(days), mock_append=mock_append, mock_delete=mock_delete):
        await ai_import_workout(user_id=1, program_name="P", raw_text="...")

    assert call_order[0] == "delete"
    assert call_order[1] == "delete"
    assert "append" in call_order[2:]


async def test_user_id_propagated_to_all_append_rows():
    """Every append_row call contains the correct user_id."""
    days = [
        WorkoutDaySummary(day_name="Push", exercises=[_ex("Bench"), _ex("OHP", order=2)]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
    ]

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days), mock_append=mock_append):
        await ai_import_workout(user_id=42, program_name="P", raw_text="...")

    for c in mock_append.call_args_list:
        assert c.args[1]["user_id"] == 42


async def test_program_name_propagated_to_workout_programs_rows():
    """program_name is written into every WorkoutPrograms row."""
    days = [WorkoutDaySummary(day_name="Day A", exercises=[_ex("Squat")])]

    mock_append = MagicMock()
    with _ai_mocks(_parsed(days), mock_append=mock_append):
        await ai_import_workout(user_id=1, program_name="My Custom Plan", raw_text="...")

    prog_calls = [c for c in mock_append.call_args_list if c.args[0] == "WorkoutPrograms"]
    assert all(c.args[1]["program_name"] == "My Custom Plan" for c in prog_calls)


# ---------------------------------------------------------------------------
# Structured-output failure
# ---------------------------------------------------------------------------


async def test_parsed_none_raises_value_error_no_sheet_writes():
    """parsed=None (model refused/timed out) raises ValueError before any sheet write."""
    mock_append = MagicMock()
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.parsed = None
    mock_client.beta.chat.completions.parse = AsyncMock(return_value=mock_completion)

    with (
        patch("api.agent.llm.get_async_client", return_value=mock_client),
        patch("api.services.workout_service.append_row", mock_append),
        patch("api.services.workout_service._delete_user_rows"),
        pytest.raises(ValueError, match="no result"),
    ):
        await ai_import_workout(user_id=1, program_name="Bad", raw_text="...")

    mock_append.assert_not_called()


async def test_no_sheet_writes_when_llm_raises():
    """If the OpenAI call raises, no append_row calls are made."""
    mock_append = MagicMock()
    mock_client = MagicMock()
    mock_client.beta.chat.completions.parse = AsyncMock(
        side_effect=ValueError("LLM returned unparseable output")
    )

    with (
        patch("api.agent.llm.get_async_client", return_value=mock_client),
        patch("api.services.workout_service.append_row", mock_append),
        patch("api.services.workout_service._delete_user_rows"),
        pytest.raises(ValueError, match="unparseable"),
    ):
        await ai_import_workout(user_id=1, program_name="Bad", raw_text="garbage")

    mock_append.assert_not_called()


# ---------------------------------------------------------------------------
# Regression: all-out-of-bounds day_index falls back to _auto_schedule
# ---------------------------------------------------------------------------


async def test_all_out_of_bounds_day_index_falls_back_to_auto_schedule():
    """
    Regression test for the 'all-Rest schedule' bug.

    When parsed.schedule is non-empty but every day_index is out of bounds for
    the days list, the filtered schedule is []. Before the fix this silently
    produced 7 Rest-only rows in WorkoutSchedules. After the fix _auto_schedule
    is called as a fallback, so at least one weekday gets a real workout day.
    """
    days = [
        WorkoutDaySummary(day_name="Legs", exercises=[_ex("Squat")]),
        WorkoutDaySummary(day_name="Push", exercises=[_ex("Bench")]),
        WorkoutDaySummary(day_name="Pull", exercises=[_ex("Row")]),
    ]
    # All day_index values (10, 11, 12) are >= len(days)==3 → all filtered out
    schedule = _sched((0, 10), (1, 11), (2, 12), (3, 10), (4, 11), (5, 12), (6, 10))

    mock_batch = MagicMock()
    mock_client = MagicMock()
    mock_completion = MagicMock()
    mock_completion.choices = [MagicMock()]
    mock_completion.choices[0].message.parsed = _parsed(days, schedule=schedule)
    mock_client.beta.chat.completions.parse = AsyncMock(return_value=mock_completion)

    with (
        patch("api.agent.llm.get_async_client", return_value=mock_client),
        patch("api.services.workout_service.append_rows_batch", mock_batch),
        patch("api.services.workout_service._delete_user_rows"),
    ):
        result = await ai_import_workout(user_id=1, program_name="PPL", raw_text="...")

    # Result should still show the correct parsed days
    assert result.program_days == 3

    # WorkoutSchedules batch write must include at least one non-Rest day
    sched_batch_calls = [
        c for c in mock_batch.call_args_list if c.args[0] == "WorkoutSchedules"
    ]
    assert len(sched_batch_calls) == 1
    written_rows = sched_batch_calls[0].args[1]
    day_names_written = [r["day_name"] for r in written_rows]
    # _auto_schedule assigns Legs→Mon, Push→Tue, Pull→Wed, Rest for Thu-Sun
    assert "Legs" in day_names_written
    assert "Push" in day_names_written
    assert "Pull" in day_names_written
    assert day_names_written.count("Rest") == 4
