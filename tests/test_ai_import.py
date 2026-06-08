"""
Tests for ai_import_workout in api/services/workout_service.py.

The LLM call (instructor / Azure OpenAI) and all sheet operations are fully
mocked — no network traffic and no writes to Google Sheets occur.

Covered scenarios
-----------------
- Happy path: parsed days + auto-scheduled schedule → correct response counts
- Happy path: parsed days + explicit schedule from LLM
- Rest-only input: single Rest day, zero exercises
- Exercise field fidelity: sets/rep_min/rep_max reach the response unchanged
- instructor error before import → no append_row calls made
"""

import os
from contextlib import ExitStack
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

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


def _ai_mocks(parsed_return, mock_append=None):
    """
    Return an ExitStack that:
      • prevents a real AsyncAzureOpenAI client from being constructed
      • makes instructor.from_openai return a client whose
        chat.completions.create resolves to parsed_return
      • replaces append_row and _delete_user_rows with no-ops (or supplied mocks)
        so no sheet writes happen
    """
    mock_instructor = MagicMock()
    mock_instructor.chat.completions.create = AsyncMock(return_value=parsed_return)

    stack = ExitStack()
    stack.enter_context(patch("api.agent.llm.get_async_client", return_value=MagicMock()))
    stack.enter_context(patch("instructor.from_openai", return_value=mock_instructor))
    stack.enter_context(
        patch("api.services.workout_service.append_row", mock_append or MagicMock())
    )
    stack.enter_context(patch("api.services.workout_service._delete_user_rows"))
    return stack


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


async def test_happy_path_auto_schedule():
    """3 training days + 2 rest days; schedule auto-assigned from plan."""
    days = [
        WorkoutDaySummary(day_name="Push", exercises=[_ex("Bench Press", order=1), _ex("OHP", order=2)]),
        WorkoutDaySummary(day_name="Pull", exercises=[_ex("Barbell Row", order=1)]),
        WorkoutDaySummary(day_name="Legs", exercises=[_ex("Squat", order=1)]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
    ]

    with _ai_mocks(_parsed(days)):
        result = await ai_import_workout(user_id=1, program_name="PPL", raw_text="Push:\nBench Press 3x8-12")

    assert result.program_name == "PPL"
    assert result.program_days == 3
    assert result.rest_days == 2
    assert result.total_exercises == 4


async def test_happy_path_explicit_schedule():
    """LLM returns an explicit weekday schedule; entries are forwarded as-is."""
    days = [
        WorkoutDaySummary(day_name="Upper", exercises=[_ex("Pull-up", order=1)]),
        WorkoutDaySummary(day_name="Lower", exercises=[_ex("Squat", order=1)]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
    ]
    schedule_entries = [
        SimpleNamespace(weekday=0, day_name="Upper"),
        SimpleNamespace(weekday=1, day_name="Lower"),
        SimpleNamespace(weekday=2, day_name="Rest"),
        SimpleNamespace(weekday=3, day_name="Upper"),
        SimpleNamespace(weekday=4, day_name="Lower"),
        SimpleNamespace(weekday=5, day_name="Rest"),
        SimpleNamespace(weekday=6, day_name="Rest"),
    ]

    with _ai_mocks(_parsed(days, schedule=schedule_entries)):
        result = await ai_import_workout(user_id=1, program_name="Upper/Lower", raw_text="anything")

    assert result.program_days == 2
    assert result.rest_days == 1
    assert result.total_exercises == 2


async def test_rest_only_input():
    """All days are Rest — program_days and total_exercises are both 0."""
    days = [WorkoutDaySummary(day_name="Rest", exercises=[])] * 7

    with _ai_mocks(_parsed(days)):
        result = await ai_import_workout(user_id=2, program_name="Deload Week", raw_text="Rest week")

    assert result.program_days == 0
    assert result.total_exercises == 0
    assert result.rest_days == 7


async def test_exercise_fields_preserved():
    """sets, rep_min, and rep_max from the LLM output reach the response unchanged."""
    days = [
        WorkoutDaySummary(day_name="Full Body", exercises=[
            _ex("Deadlift", sets=5, rep_min=3, rep_max=5, order=1),
        ]),
    ]

    with _ai_mocks(_parsed(days)):
        result = await ai_import_workout(user_id=1, program_name="Strength", raw_text="Deadlift 5x3-5")

    ex = result.days[0].exercises[0]
    assert ex.exercise_name == "Deadlift"
    assert ex.sets == 5
    assert ex.rep_min == 3
    assert ex.rep_max == 5


async def test_no_sheet_writes_when_llm_raises():
    """If instructor raises (validation failure), no append_row calls are made."""
    mock_append = MagicMock()
    mock_instructor = MagicMock()
    mock_instructor.chat.completions.create = AsyncMock(
        side_effect=ValueError("LLM returned unparseable output")
    )

    with (
        ExitStack() as stack
    ):
        stack.enter_context(patch("api.agent.llm.get_async_client", return_value=MagicMock()))
        stack.enter_context(patch("instructor.from_openai", return_value=mock_instructor))
        stack.enter_context(patch("api.services.workout_service.append_row", mock_append))
        stack.enter_context(patch("api.services.workout_service._delete_user_rows"))

        with pytest.raises(ValueError, match="unparseable"):
            await ai_import_workout(user_id=1, program_name="Bad", raw_text="garbage")

    mock_append.assert_not_called()
