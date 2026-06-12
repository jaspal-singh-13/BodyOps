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

from unittest.mock import AsyncMock, MagicMock

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
    workout_importer=None,
    plans_lister=None,
    plan_switcher=None,
    coaching_generator=None,
    weekly_review_generator=None,
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
        workout_importer: Optional async mock for AI workout import.
        plans_lister: Optional mock for listing workout plans.
        plan_switcher: Optional mock for switching workout plans.
        coaching_generator: Optional async mock for daily coaching generation.
        weekly_review_generator: Optional async mock for weekly review generation.

    Returns:
        ``AgentDeps`` ready to be passed to a tool via a mock ``RunContext``.
    """
    _default_coaching = {"date": "2026-06-08", "summary": "Good job", "wins": [], "focus": [], "next_step": "Keep going", "generated_at": "2026-06-08T00:00:00+00:00", "cached": False}
    _default_weekly = {"week_start": "2026-06-02", "week_end": "2026-06-08", "summary": "Solid week", "wins": [], "focus": [], "next_step": "Keep going", "generated_at": "2026-06-08T00:00:00+00:00", "cached": False}
    return AgentDeps(
        user_id=user_id,
        timezone="UTC",
        event_queue=queue,
        weight_logger=weight_logger or MagicMock(return_value={"weight_kg": 85.5, "date": "2026-06-08"}),
        trend_getter=trend_getter or MagicMock(return_value={"moving_avg": [], "total_loss_kg": None, "projected_goal_date": None}),
        today_workout_getter=today_workout_getter or MagicMock(return_value={"day_name": "Push", "is_rest_day": False, "exercises": []}),
        set_logger=set_logger or MagicMock(return_value={"session_id": "1-2026-06-08", "set_number": 1}),
        progression_getter=progression_getter or MagicMock(return_value={"exercise_name": "Bench Press", "last_5_sessions": [], "suggestion": {"weight_kg": None, "reps": None, "note": "first session"}}),
        workout_importer=workout_importer or AsyncMock(return_value={}),
        plans_lister=plans_lister or MagicMock(return_value={"plans": []}),
        plan_switcher=plan_switcher or MagicMock(return_value={"activated": True, "plan_name": "Test"}),
        nutrition_getter=MagicMock(return_value={"calories": 0, "meals_count": 0}),
        meal_saver=AsyncMock(return_value={"meal_id": "test-id"}),
        meal_analyzer=AsyncMock(return_value={"title": "Test", "detected": []}),
        task_status_getter=MagicMock(return_value={"date": "2026-06-08", "tasks": [], "total": 0, "completed": 0, "percentage": 0.0}),
        task_completer=MagicMock(return_value={"date": "2026-06-08", "tasks": [], "total": 0, "completed": 0, "percentage": 0.0}),
        coaching_generator=coaching_generator or AsyncMock(return_value=_default_coaching),
        weekly_review_generator=weekly_review_generator or AsyncMock(return_value=_default_weekly),
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


# ── generate_daily_coaching tool ─────────────────────────────────────────────

class TestGenerateDailyCoachingTool:
    @pytest.mark.asyncio
    async def test_emits_tool_call_then_tool_result(self):
        """Queue receives exactly 2 events with correct type and tool name."""
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_deps(1, queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.generate_daily_coaching(ctx)

        assert queue.qsize() == 2
        call_evt = await queue.get()
        result_evt = await queue.get()
        assert call_evt["type"] == "tool_call"
        assert call_evt["tool"] == "generate_daily_coaching"
        assert call_evt["args"] == {}
        assert result_evt["type"] == "tool_result"
        assert result_evt["tool"] == "generate_daily_coaching"

    @pytest.mark.asyncio
    async def test_delegates_to_coaching_generator(self):
        """coaching_generator callable is awaited exactly once with no arguments."""
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        mock_generator = AsyncMock(return_value={"summary": "test", "wins": [], "focus": [], "next_step": "go"})
        deps = _make_deps(1, queue, coaching_generator=mock_generator)
        ctx = _make_ctx(deps)

        await api.agent.tools.generate_daily_coaching(ctx)

        mock_generator.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_returns_coaching_dict(self):
        """Tool returns the exact dict from the coaching_generator callable."""
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        expected = {
            "date": "2026-06-13",
            "summary": "You crushed your protein target.",
            "wins": ["Hit protein target"],
            "focus": ["Log weight daily"],
            "next_step": "Weigh in tomorrow morning",
            "generated_at": "2026-06-13T00:00:00+00:00",
            "cached": False,
        }
        deps = _make_deps(1, queue, coaching_generator=AsyncMock(return_value=expected))
        ctx = _make_ctx(deps)

        result = await api.agent.tools.generate_daily_coaching(ctx)

        assert result == expected


# ── generate_weekly_review tool ──────────────────────────────────────────────

class TestGenerateWeeklyReviewTool:
    @pytest.mark.asyncio
    async def test_emits_tool_call_then_tool_result(self):
        """Queue receives exactly 2 events with correct type and tool name."""
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        deps = _make_deps(1, queue)
        ctx = _make_ctx(deps)

        await api.agent.tools.generate_weekly_review(ctx)

        assert queue.qsize() == 2
        call_evt = await queue.get()
        result_evt = await queue.get()
        assert call_evt["type"] == "tool_call"
        assert call_evt["tool"] == "generate_weekly_review"
        assert call_evt["args"] == {}
        assert result_evt["type"] == "tool_result"
        assert result_evt["tool"] == "generate_weekly_review"

    @pytest.mark.asyncio
    async def test_delegates_to_weekly_review_generator(self):
        """weekly_review_generator callable is awaited exactly once with no arguments."""
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        mock_generator = AsyncMock(return_value={"summary": "great week", "wins": [], "focus": [], "next_step": "keep going"})
        deps = _make_deps(1, queue, weekly_review_generator=mock_generator)
        ctx = _make_ctx(deps)

        await api.agent.tools.generate_weekly_review(ctx)

        mock_generator.assert_awaited_once_with()

    @pytest.mark.asyncio
    async def test_returns_weekly_review_dict(self):
        """Tool returns the exact dict from the weekly_review_generator callable."""
        import api.agent.tools  # noqa: F401

        queue: asyncio.Queue = asyncio.Queue()
        expected = {
            "week_start": "2026-06-09",
            "week_end": "2026-06-15",
            "summary": "Consistent week — 5 out of 7 days on target.",
            "wins": ["Hit protein 5/7 days"],
            "focus": ["Weekend logging"],
            "next_step": "Plan Sunday meals in advance",
            "generated_at": "2026-06-13T00:00:00+00:00",
            "cached": False,
        }
        deps = _make_deps(1, queue, weekly_review_generator=AsyncMock(return_value=expected))
        ctx = _make_ctx(deps)

        result = await api.agent.tools.generate_weekly_review(ctx)

        assert result == expected
