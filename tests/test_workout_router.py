"""
Tests for the workout system API routes and agent tools.

Router tests: POST /workouts/import, GET /workouts/today, POST /workouts/log,
              POST /workouts/complete, GET /workouts/progression, GET /workouts/history

Agent tool tests: get_today_workout, log_workout_set, get_progression_target
"""

import asyncio
import os
from unittest.mock import AsyncMock, MagicMock, patch

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-sheet-id")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

import pytest

from api.models.workout import (
    ExerciseProgressionResponse,
    LogSetResponse,
    ProgressionSuggestion,
    TodayWorkoutResponse,
    WorkoutHistoryResponse,
    WorkoutImportResponse,
    WorkoutDaySummary,
)

# ---------------------------------------------------------------------------
# Fixture responses
# ---------------------------------------------------------------------------

IMPORT_RESPONSE = WorkoutImportResponse(
    program_name="PPL v1",
    program_days=3,
    rest_days=4,
    total_exercises=6,
    days=[
        WorkoutDaySummary(day_name="Push", exercises=[]),
        WorkoutDaySummary(day_name="Pull", exercises=[]),
        WorkoutDaySummary(day_name="Legs", exercises=[]),
        WorkoutDaySummary(day_name="Rest", exercises=[]),
    ],
)

TODAY_RESPONSE = TodayWorkoutResponse(
    date="2026-06-08",
    day_name="Push",
    is_rest_day=False,
    exercises=[],
    estimated_duration_min=11,
)

REST_DAY_RESPONSE = TodayWorkoutResponse(
    date="2026-06-08",
    day_name="Rest",
    is_rest_day=True,
    exercises=[],
    estimated_duration_min=0,
)

LOG_SET_RESPONSE = LogSetResponse(
    session_id="1-2026-06-08",
    exercise_name="Bench Press",
    set_number=1,
    weight_kg=60.0,
    reps=12,
    logged_at="2026-06-08T10:00:00+00:00",
    suggestion=ProgressionSuggestion(weight_kg=62.5, reps=8, note="increase weight"),
)

PROGRESSION_RESPONSE = ExerciseProgressionResponse(
    exercise_name="Bench Press",
    last_5_sessions=[
        {"date": "2026-06-08", "sets": [{"set_number": 1, "weight_kg": 60.0, "reps": 12}]}
    ],
    suggestion=ProgressionSuggestion(weight_kg=62.5, reps=8, note="increase weight"),
)

HISTORY_RESPONSE = WorkoutHistoryResponse(
    sessions=[
        {
            "session_id": "1-2026-06-08",
            "date": "2026-06-08",
            "day_name": "Push",
            "started_at": "2026-06-08T10:00:00+00:00",
            "completed_at": "2026-06-08T11:00:00+00:00",
        }
    ]
)

IMPORT_PAYLOAD = {
    "plan_text": "Push:\nBench Press 3x8-12\n",
    "schedule_text": "Mon - Push\n",
    "program_name": "PPL v1",
}

LOG_SET_PAYLOAD = {
    "date": "2026-06-08",
    "exercise_name": "Bench Press",
    "weight_kg": 60.0,
    "reps": 12,
    "day_name": "Push",
}


# ---------------------------------------------------------------------------
# POST /workouts/import
# ---------------------------------------------------------------------------


class TestPostWorkoutsImport:
    def test_import_success(self, client, auth_headers):
        with (
            patch("api.routers.workouts.parse_workout_import", return_value=([], [])),
            patch("api.routers.workouts.import_workout", return_value=IMPORT_RESPONSE),
        ):
            resp = client.post("/workouts/import", json=IMPORT_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["program_name"] == "PPL v1"
        assert data["program_days"] == 3
        assert data["rest_days"] == 4
        assert data["total_exercises"] == 6

    def test_import_parse_error_returns_422(self, client, auth_headers):
        from api.services.workout_parser import WorkoutParseError
        with patch(
            "api.routers.workouts.parse_workout_import",
            side_effect=WorkoutParseError("unrecognised line: 'bad'", 2),
        ):
            resp = client.post("/workouts/import", json=IMPORT_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 422
        assert "line 2" in resp.json()["detail"]

    def test_import_missing_plan_text_returns_422(self, client, auth_headers):
        resp = client.post(
            "/workouts/import",
            json={"schedule_text": "", "program_name": "PPL v1"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_import_no_auth_returns_403(self, client):
        resp = client.post("/workouts/import", json=IMPORT_PAYLOAD)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /workouts/today
# ---------------------------------------------------------------------------


class TestGetWorkoutsToday:
    def test_today_returns_workout(self, client, auth_headers):
        with patch("api.routers.workouts.get_today_workout", return_value=TODAY_RESPONSE):
            resp = client.get("/workouts/today", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["day_name"] == "Push"
        assert data["is_rest_day"] is False
        assert "exercises" in data
        assert "estimated_duration_min" in data

    def test_today_returns_rest_day(self, client, auth_headers):
        with patch("api.routers.workouts.get_today_workout", return_value=REST_DAY_RESPONSE):
            resp = client.get("/workouts/today", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["is_rest_day"] is True
        assert data["exercises"] == []
        assert data["estimated_duration_min"] == 0

    def test_today_no_auth_returns_403(self, client):
        resp = client.get("/workouts/today")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /workouts/log
# ---------------------------------------------------------------------------


class TestPostWorkoutsLog:
    def test_log_set_success(self, client, auth_headers):
        with patch("api.routers.workouts.log_set", return_value=LOG_SET_RESPONSE):
            resp = client.post("/workouts/log", json=LOG_SET_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["session_id"] == "1-2026-06-08"
        assert data["set_number"] == 1
        assert data["suggestion"]["note"] == "increase weight"
        assert data["suggestion"]["weight_kg"] == 62.5

    def test_log_set_missing_exercise_name_returns_422(self, client, auth_headers):
        payload = {k: v for k, v in LOG_SET_PAYLOAD.items() if k != "exercise_name"}
        resp = client.post("/workouts/log", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_log_set_invalid_weight_type_returns_422(self, client, auth_headers):
        payload = {**LOG_SET_PAYLOAD, "weight_kg": "heavy"}
        resp = client.post("/workouts/log", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_log_set_no_auth_returns_403(self, client):
        resp = client.post("/workouts/log", json=LOG_SET_PAYLOAD)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /workouts/complete
# ---------------------------------------------------------------------------


class TestPostWorkoutsComplete:
    def test_complete_session_returns_204(self, client, auth_headers):
        with patch("api.routers.workouts.complete_session", return_value=None):
            resp = client.post(
                "/workouts/complete",
                json={"date": "2026-06-08"},
                headers=auth_headers,
            )
        assert resp.status_code == 204

    def test_complete_no_auth_returns_403(self, client):
        resp = client.post("/workouts/complete", json={"date": "2026-06-08"})
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /workouts/progression
# ---------------------------------------------------------------------------


class TestGetWorkoutsProgression:
    def test_get_progression_returns_data(self, client, auth_headers):
        with patch("api.routers.workouts.get_progression", return_value=PROGRESSION_RESPONSE):
            resp = client.get(
                "/workouts/progression?exercise=Bench+Press",
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["exercise_name"] == "Bench Press"
        assert len(data["last_5_sessions"]) == 1
        assert data["suggestion"]["note"] == "increase weight"

    def test_get_progression_no_auth_returns_403(self, client):
        resp = client.get("/workouts/progression?exercise=Bench+Press")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# GET /workouts/history
# ---------------------------------------------------------------------------


class TestGetWorkoutsHistory:
    def test_get_history_returns_sessions(self, client, auth_headers):
        with patch("api.routers.workouts.get_history", return_value=HISTORY_RESPONSE):
            resp = client.get("/workouts/history", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["sessions"]) == 1
        assert data["sessions"][0]["day_name"] == "Push"

    def test_get_history_empty_returns_empty_list(self, client, auth_headers):
        with patch(
            "api.routers.workouts.get_history",
            return_value=WorkoutHistoryResponse(sessions=[]),
        ):
            resp = client.get("/workouts/history", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json()["sessions"] == []

    def test_get_history_no_auth_returns_403(self, client):
        resp = client.get("/workouts/history")
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# POST /workouts/ai-import
# ---------------------------------------------------------------------------

AI_IMPORT_PAYLOAD = {
    "raw_text": "Monday: Chest day\nBench Press 4 sets 8-10 reps",
    "program_name": "PPL v1",
}


class TestPostWorkoutsAiImport:
    def test_ai_import_success(self, client, auth_headers):
        with patch("api.routers.workouts.ai_import_workout", new_callable=AsyncMock, return_value=IMPORT_RESPONSE):
            resp = client.post("/workouts/ai-import", json=AI_IMPORT_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["program_name"] == "PPL v1"
        assert data["program_days"] == 3
        assert data["rest_days"] == 4
        assert data["total_exercises"] == 6

    def test_ai_import_parse_error_returns_422(self, client, auth_headers):
        from api.services.workout_parser import WorkoutParseError
        with patch(
            "api.routers.workouts.ai_import_workout",
            new_callable=AsyncMock,
            side_effect=WorkoutParseError("unrecognised line: 'bad'", 3),
        ):
            resp = client.post("/workouts/ai-import", json=AI_IMPORT_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 422
        assert "line 3" in resp.json()["detail"]

    def test_ai_import_no_auth_returns_403(self, client):
        resp = client.post("/workouts/ai-import", json=AI_IMPORT_PAYLOAD)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# Agent tools — workout
# ---------------------------------------------------------------------------


def _make_workout_deps(queue: asyncio.Queue) -> "AgentDeps":
    from api.agent.deps import AgentDeps
    return AgentDeps(
        user_id=1,
        event_queue=queue,
        weight_logger=MagicMock(return_value={}),
        trend_getter=MagicMock(return_value={}),
        today_workout_getter=MagicMock(
            return_value={"day_name": "Push", "is_rest_day": False, "exercises": [], "estimated_duration_min": 11}
        ),
        set_logger=MagicMock(
            return_value={"session_id": "1-2026-06-08", "set_number": 1, "suggestion": {"note": "first session"}}
        ),
        progression_getter=MagicMock(
            return_value={"exercise_name": "Bench Press", "last_5_sessions": [], "suggestion": {"note": "first session"}}
        ),
        workout_importer=AsyncMock(return_value=IMPORT_RESPONSE.model_dump()),
    )


def _make_ctx(deps):
    ctx = MagicMock()
    ctx.deps = deps
    return ctx


class TestGetTodayWorkoutTool:
    @pytest.mark.asyncio
    async def test_emits_tool_call_then_tool_result(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_workout_deps(queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.get_today_workout(ctx)

        assert queue.qsize() == 2
        call_evt = await queue.get()
        result_evt = await queue.get()
        assert call_evt["type"] == "tool_call"
        assert call_evt["tool"] == "get_today_workout"
        assert result_evt["type"] == "tool_result"

    @pytest.mark.asyncio
    async def test_delegates_to_today_workout_getter(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_workout_deps(queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.get_today_workout(ctx)

        deps.today_workout_getter.assert_called_once_with()


class TestLogWorkoutSetTool:
    @pytest.mark.asyncio
    async def test_emits_tool_call_then_tool_result(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_workout_deps(queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.log_workout_set(ctx, "Bench Press", 60.0, 10)

        assert queue.qsize() == 2
        call_evt = await queue.get()
        assert call_evt["type"] == "tool_call"
        assert call_evt["args"] == {"exercise_name": "Bench Press", "weight_kg": 60.0, "reps": 10}

    @pytest.mark.asyncio
    async def test_delegates_to_set_logger_with_correct_args(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_workout_deps(queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.log_workout_set(ctx, "Squat", 80.0, 8)

        deps.set_logger.assert_called_once_with("Squat", 80.0, 8)


class TestGetProgressionTargetTool:
    @pytest.mark.asyncio
    async def test_emits_tool_call_then_tool_result(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_workout_deps(queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.get_progression_target(ctx, "Bench Press")

        assert queue.qsize() == 2
        call_evt = await queue.get()
        assert call_evt["tool"] == "get_progression_target"
        assert call_evt["args"] == {"exercise_name": "Bench Press"}

    @pytest.mark.asyncio
    async def test_delegates_to_progression_getter(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_workout_deps(queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.get_progression_target(ctx, "Deadlift")

        deps.progression_getter.assert_called_once_with("Deadlift")


class TestImportWorkoutFromTextTool:
    @pytest.mark.asyncio
    async def test_emits_tool_call_then_tool_result(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_workout_deps(queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.import_workout_from_text(ctx, "Monday: Chest\nBench Press 3x8", "PPL v1")

        assert queue.qsize() == 2
        call_evt = await queue.get()
        result_evt = await queue.get()
        assert call_evt["type"] == "tool_call"
        assert call_evt["tool"] == "import_workout_from_text"
        assert call_evt["args"]["program_name"] == "PPL v1"
        assert result_evt["type"] == "tool_result"

    @pytest.mark.asyncio
    async def test_delegates_to_workout_importer(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_workout_deps(queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.import_workout_from_text(ctx, "raw plan text", "My PPL")

        deps.workout_importer.assert_awaited_once_with("raw plan text", "My PPL")
