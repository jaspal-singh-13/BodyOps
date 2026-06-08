"""
Unit tests for agent tools — verifies event emission and injected service delegation.

Tests confirm that each tool:
    1. Pushes a ``tool_call`` event to the queue before executing.
    2. Pushes a ``tool_result`` event to the queue after executing.
    3. Delegates to the correct injected callable (``weight_logger`` / ``trend_getter``).
    4. Returns the callable's return value.

No real Google Sheets or Azure OpenAI calls are made — services are injected
as ``MagicMock`` callables via ``AgentDeps``.
"""

import asyncio
import os

# Set env vars before any agent.* import to satisfy module-level LLM factory calls
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-id")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

from unittest.mock import MagicMock

import pytest

from api.agent.deps import AgentDeps


def _make_deps(
    user_id: int,
    queue: asyncio.Queue,
    weight_logger=None,
    trend_getter=None,
    today_workout_getter=None,
    set_logger=None,
    progression_getter=None,
) -> AgentDeps:
    """
    Build an ``AgentDeps`` instance with mock service callables.

    Args:
        user_id: User ID to embed in deps.
        queue: Async queue for event capture.
        weight_logger: Optional mock; defaults to one returning a sample entry dict.
        trend_getter: Optional mock; defaults to one returning an empty trend dict.
        today_workout_getter: Optional mock for workout tool.
        set_logger: Optional mock for workout set logging.
        progression_getter: Optional mock for progression data.

    Returns:
        ``AgentDeps`` ready to be passed to a tool via a mock ``RunContext``.
    """
    return AgentDeps(
        user_id=user_id,
        event_queue=queue,
        weight_logger=weight_logger or MagicMock(return_value={"weight_kg": 85.5, "date": "2026-06-08"}),
        trend_getter=trend_getter or MagicMock(return_value={"moving_avg": [], "total_loss_kg": None, "projected_goal_date": None}),
        today_workout_getter=today_workout_getter or MagicMock(return_value={"day_name": "Push", "is_rest_day": False, "exercises": []}),
        set_logger=set_logger or MagicMock(return_value={"session_id": "1-2026-06-08", "set_number": 1}),
        progression_getter=progression_getter or MagicMock(return_value={"exercise_name": "Bench Press", "last_5_sessions": [], "suggestion": {"weight_kg": None, "reps": None, "note": "first session"}}),
    )


def _make_ctx(deps: AgentDeps) -> MagicMock:
    """
    Build a minimal mock ``RunContext`` carrying the given deps.

    Pydantic AI passes a ``RunContext[AgentDeps]`` to each tool. We replicate
    the ``ctx.deps`` attribute access pattern here.

    Args:
        deps: ``AgentDeps`` instance to attach.

    Returns:
        ``MagicMock`` with ``.deps`` set.
    """
    ctx = MagicMock()
    ctx.deps = deps
    return ctx


# ── log_weight tool ──────────────────────────────────────────────────────────

class TestLogWeightTool:
    @pytest.mark.asyncio
    async def test_emits_tool_call_then_tool_result(self):
        import api.agent.tools  # noqa: F401 — triggers @agent.tool registration

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_deps(1, queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.log_weight(ctx, "2026-06-08", 85.5)

        assert queue.qsize() == 2
        call_evt = await queue.get()
        result_evt = await queue.get()
        assert call_evt["type"] == "tool_call"
        assert call_evt["tool"] == "log_weight"
        assert call_evt["args"] == {"date": "2026-06-08", "weight_kg": 85.5}
        assert result_evt["type"] == "tool_result"
        assert result_evt["tool"] == "log_weight"

    @pytest.mark.asyncio
    async def test_delegates_to_weight_logger_with_correct_args(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        weight_logger = MagicMock(return_value={"weight_kg": 90.0, "date": "2026-06-08"})
        deps = _make_deps(2, queue, weight_logger=weight_logger)
        ctx = _make_ctx(deps)

        await api.agent.tools.log_weight(ctx, "2026-06-08", 90.0)

        weight_logger.assert_called_once_with("2026-06-08", 90.0)

    @pytest.mark.asyncio
    async def test_returns_dict(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        expected = {"weight_kg": 75.0, "date": "2026-06-08"}
        deps = _make_deps(1, queue, weight_logger=MagicMock(return_value=expected))
        ctx = _make_ctx(deps)

        result = await api.agent.tools.log_weight(ctx, "2026-06-08", 75.0)

        assert result == expected


# ── get_weight_trend tool ────────────────────────────────────────────────────

class TestGetWeightTrendTool:
    @pytest.mark.asyncio
    async def test_emits_tool_call_then_tool_result(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_deps(1, queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.get_weight_trend(ctx)

        assert queue.qsize() == 2
        call_evt = await queue.get()
        result_evt = await queue.get()
        assert call_evt["type"] == "tool_call"
        assert call_evt["tool"] == "get_weight_trend"
        assert call_evt["args"] == {}
        assert result_evt["type"] == "tool_result"

    @pytest.mark.asyncio
    async def test_delegates_to_trend_getter(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        trend_getter = MagicMock(return_value={"moving_avg": [], "total_loss_kg": 5.0, "projected_goal_date": None})
        deps = _make_deps(1, queue, trend_getter=trend_getter)
        ctx = _make_ctx(deps)

        await api.agent.tools.get_weight_trend(ctx)

        trend_getter.assert_called_once_with()

    @pytest.mark.asyncio
    async def test_returns_dict(self):
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        expected = {"moving_avg": [], "total_loss_kg": None, "projected_goal_date": None}
        deps = _make_deps(1, queue, trend_getter=MagicMock(return_value=expected))
        ctx = _make_ctx(deps)

        result = await api.agent.tools.get_weight_trend(ctx)

        assert result == expected
        assert "moving_avg" in result
