"""
Unit and integration tests for api/services/coach_service.py and
api/routers/coach.py (Phase 6 — AI Coach).

Service tests (mocked gspread + OpenAI):
    TestGenerateDailyCoaching
        - test_no_cached_insight_calls_openai
        - test_cached_insight_within_1hr_skips_openai
        - test_stale_cache_over_1hr_regenerates
        - test_saves_correct_fields_to_sheet_on_fresh_generate
        - test_stale_cache_updates_row_not_appends
        - test_gathers_data_before_calling_openai
        - test_response_shape_has_required_keys
        - test_user_id_scoping_ignores_other_users_cache

    TestGenerateWeeklyReview
        - test_no_cached_review_calls_openai
        - test_cached_review_returns_without_openai
        - test_weekly_window_spans_mon_to_sun
        - test_response_shape

Router tests (FastAPI TestClient + patched service):
    TestGetCoachDailyEndpoint
        - test_returns_200_with_coaching_shape
        - test_returns_401_without_auth
        - test_empty_state_no_data_does_not_500

    TestGetCoachWeeklyEndpoint
        - test_returns_200_with_weekly_shape
        - test_returns_401_without_auth
"""

import json
import os
from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-id")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

USER_ID = 1
TODAY = datetime.now(timezone.utc).date().isoformat()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _fake_openai_client(summary="Great day!", wins=None, focus=None, next_step="Keep going"):
    """
    Return a mock Azure OpenAI client whose ``beta.chat.completions.parse``
    resolves to a fake ``_CoachingSchema``-like namespace.
    """
    wins = wins or ["Hit protein target"]
    focus = focus or ["Log weight daily"]
    parsed = SimpleNamespace(
        summary=summary,
        wins=wins,
        focus=focus,
        next_step=next_step,
    )
    completion = MagicMock()
    completion.choices = [MagicMock()]
    completion.choices[0].message.parsed = parsed
    client = MagicMock()
    client.beta.chat.completions.parse = AsyncMock(return_value=completion)
    return client


def _fresh_ts(minutes_ago: int = 30) -> str:
    """Return an ISO UTC timestamp that is ``minutes_ago`` minutes in the past."""
    return (datetime.now(timezone.utc) - timedelta(minutes=minutes_ago)).isoformat()


def _stale_ts() -> str:
    """Return an ISO UTC timestamp that is 2 hours in the past (outside 60 min cache)."""
    return (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()


def _make_insight_row(
    user_id=USER_ID,
    insight_type="daily",
    date=None,
    generated_at=None,
    summary="Good job",
    wins_json='["Win 1"]',
    focus_json='["Focus 1"]',
    next_step="Keep it up",
):
    """Build a minimal CoachInsights sheet row dict."""
    return {
        "user_id": str(user_id),
        "id": "insight-1",
        "date": date or TODAY,
        "type": insight_type,
        "summary": summary,
        "wins_json": wins_json,
        "focus_json": focus_json,
        "next_step": next_step,
        "generated_at": generated_at or _fresh_ts(),
    }


# ---------------------------------------------------------------------------
# TestGenerateDailyCoaching
# ---------------------------------------------------------------------------


class TestGenerateDailyCoaching:
    @pytest.mark.asyncio
    async def test_no_cached_insight_calls_openai(self):
        """When CoachInsights has no row for today → OpenAI is called once."""
        mock_client = _fake_openai_client()
        with (
            patch("api.services.coach_service.read_rows", return_value=[]),
            patch("api.services.coach_service.append_row") as mock_append,
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch("api.services.coach_service._gather_daily_context", return_value="context"),
        ):
            from api.services.coach_service import generate_daily_coaching

            result = await generate_daily_coaching(USER_ID, "UTC")

        mock_client.beta.chat.completions.parse.assert_awaited_once()
        mock_append.assert_called_once()
        assert result.cached is False

    @pytest.mark.asyncio
    async def test_cached_insight_within_1hr_skips_openai(self):
        """Existing row generated 30 min ago → OpenAI NOT called, cached=True returned."""
        row = _make_insight_row(generated_at=_fresh_ts(30))
        mock_client = _fake_openai_client()
        with (
            patch("api.services.coach_service.read_rows", return_value=[row]),
            patch("api.agent.llm.get_async_client", return_value=mock_client),
        ):
            from api.services.coach_service import generate_daily_coaching

            result = await generate_daily_coaching(USER_ID, "UTC")

        mock_client.beta.chat.completions.parse.assert_not_awaited()
        assert result.cached is True
        assert result.summary == "Good job"

    @pytest.mark.asyncio
    async def test_stale_cache_over_1hr_regenerates(self):
        """Existing row generated 2 hours ago → OpenAI called, row updated (not appended again)."""
        stale_row = _make_insight_row(generated_at=_stale_ts())
        mock_client = _fake_openai_client(summary="Fresh coaching")
        with (
            patch("api.services.coach_service.read_rows", return_value=[stale_row]),
            patch("api.services.coach_service.update_row") as mock_update,
            patch("api.services.coach_service.append_row") as mock_append,
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch("api.services.coach_service._gather_daily_context", return_value="context"),
        ):
            from api.services.coach_service import generate_daily_coaching

            result = await generate_daily_coaching(USER_ID, "UTC")

        mock_client.beta.chat.completions.parse.assert_awaited_once()
        mock_update.assert_called_once()
        mock_append.assert_not_called()
        assert result.cached is False
        assert result.summary == "Fresh coaching"

    @pytest.mark.asyncio
    async def test_saves_correct_fields_to_sheet_on_fresh_generate(self):
        """Appended row contains all required CoachInsights fields."""
        mock_client = _fake_openai_client(
            summary="You nailed it",
            wins=["Hit protein"],
            focus=["More cardio"],
            next_step="Sleep 8h",
        )
        saved_row: dict = {}

        def capture_append(tab, row):
            saved_row.update(row)

        with (
            patch("api.services.coach_service.read_rows", return_value=[]),
            patch("api.services.coach_service.append_row", side_effect=capture_append),
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch("api.services.coach_service._gather_daily_context", return_value="ctx"),
        ):
            from api.services.coach_service import generate_daily_coaching

            await generate_daily_coaching(USER_ID, "UTC")

        assert saved_row["user_id"] == USER_ID
        assert saved_row["type"] == "daily"
        assert saved_row["date"] == TODAY
        assert saved_row["summary"] == "You nailed it"
        assert json.loads(saved_row["wins_json"]) == ["Hit protein"]
        assert json.loads(saved_row["focus_json"]) == ["More cardio"]
        assert saved_row["next_step"] == "Sleep 8h"
        assert "generated_at" in saved_row
        assert "id" in saved_row

    @pytest.mark.asyncio
    async def test_stale_cache_updates_row_not_appends(self):
        """Stale row triggers update_row, never append_row."""
        stale_row = _make_insight_row(generated_at=_stale_ts())
        mock_client = _fake_openai_client()
        with (
            patch("api.services.coach_service.read_rows", return_value=[stale_row]),
            patch("api.services.coach_service.update_row") as mock_update,
            patch("api.services.coach_service.append_row") as mock_append,
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch("api.services.coach_service._gather_daily_context", return_value="ctx"),
        ):
            from api.services.coach_service import generate_daily_coaching

            await generate_daily_coaching(USER_ID, "UTC")

        mock_update.assert_called_once()
        mock_append.assert_not_called()

    @pytest.mark.asyncio
    async def test_gathers_data_before_calling_openai(self):
        """_gather_daily_context is called before OpenAI when no cache exists."""
        mock_client = _fake_openai_client()
        with (
            patch("api.services.coach_service.read_rows", return_value=[]),
            patch("api.services.coach_service.append_row"),
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch(
                "api.services.coach_service._gather_daily_context",
                return_value="gathered context",
            ) as mock_gather,
        ):
            from api.services.coach_service import generate_daily_coaching

            await generate_daily_coaching(USER_ID, "UTC")

        mock_gather.assert_called_once_with(USER_ID, TODAY, "UTC")
        # Verify the gathered context was passed to OpenAI
        call_kwargs = mock_client.beta.chat.completions.parse.call_args
        messages = call_kwargs.kwargs.get("messages") or call_kwargs.args[0] if call_kwargs.args else None
        # Check the user message contains the gathered context
        if call_kwargs.kwargs.get("messages"):
            user_msg = next(m for m in call_kwargs.kwargs["messages"] if m["role"] == "user")
            assert user_msg["content"] == "gathered context"

    @pytest.mark.asyncio
    async def test_response_shape_has_required_keys(self):
        """Response contains all required CoachingResponse fields."""
        mock_client = _fake_openai_client()
        with (
            patch("api.services.coach_service.read_rows", return_value=[]),
            patch("api.services.coach_service.append_row"),
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch("api.services.coach_service._gather_daily_context", return_value="ctx"),
        ):
            from api.services.coach_service import generate_daily_coaching

            result = await generate_daily_coaching(USER_ID, "UTC")

        assert isinstance(result.summary, str) and result.summary
        assert isinstance(result.wins, list)
        assert isinstance(result.focus, list)
        assert isinstance(result.next_step, str) and result.next_step
        assert result.date == TODAY
        assert isinstance(result.generated_at, str)
        assert isinstance(result.cached, bool)

    @pytest.mark.asyncio
    async def test_user_id_scoping_ignores_other_users_cache(self):
        """A cached row belonging to user_id=2 is not a cache hit for user_id=1."""
        other_user_row = _make_insight_row(user_id=2, generated_at=_fresh_ts(5))
        mock_client = _fake_openai_client()
        with (
            patch("api.services.coach_service.read_rows", return_value=[other_user_row]),
            patch("api.services.coach_service.append_row") as mock_append,
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch("api.services.coach_service._gather_daily_context", return_value="ctx"),
        ):
            from api.services.coach_service import generate_daily_coaching

            result = await generate_daily_coaching(USER_ID, "UTC")

        mock_client.beta.chat.completions.parse.assert_awaited_once()
        mock_append.assert_called_once()
        assert result.cached is False


# ---------------------------------------------------------------------------
# TestGenerateWeeklyReview
# ---------------------------------------------------------------------------


class TestGenerateWeeklyReview:
    @pytest.mark.asyncio
    async def test_no_cached_review_calls_openai(self):
        """No weekly row in CoachInsights → OpenAI is called once."""
        mock_client = _fake_openai_client(summary="Great week!")
        with (
            patch("api.services.coach_service.read_rows", return_value=[]),
            patch("api.services.coach_service.append_row") as mock_append,
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch("api.services.coach_service._gather_weekly_context", return_value="ctx"),
        ):
            from api.services.coach_service import generate_weekly_review

            result = await generate_weekly_review(USER_ID, "UTC")

        mock_client.beta.chat.completions.parse.assert_awaited_once()
        mock_append.assert_called_once()
        assert result.cached is False
        assert result.summary == "Great week!"

    @pytest.mark.asyncio
    async def test_cached_review_returns_without_openai(self):
        """Existing weekly row for this week → OpenAI NOT called."""
        from api.services.coach_service import _current_week_bounds

        week_start, _ = _current_week_bounds(TODAY)
        row = _make_insight_row(
            insight_type="weekly",
            date=week_start,
            summary="Solid week",
        )
        mock_client = _fake_openai_client()
        with (
            patch("api.services.coach_service.read_rows", return_value=[row]),
            patch("api.agent.llm.get_async_client", return_value=mock_client),
        ):
            from api.services.coach_service import generate_weekly_review

            result = await generate_weekly_review(USER_ID, "UTC")

        mock_client.beta.chat.completions.parse.assert_not_awaited()
        assert result.cached is True
        assert result.summary == "Solid week"

    @pytest.mark.asyncio
    async def test_weekly_window_spans_mon_to_sun(self):
        """_gather_weekly_context is called with the correct Mon-Sun bounds."""
        mock_client = _fake_openai_client()
        with (
            patch("api.services.coach_service.read_rows", return_value=[]),
            patch("api.services.coach_service.append_row"),
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch(
                "api.services.coach_service._gather_weekly_context",
                return_value="ctx",
            ) as mock_gather,
        ):
            from api.services.coach_service import generate_weekly_review, _current_week_bounds

            await generate_weekly_review(USER_ID, "UTC")

        expected_start, expected_end = _current_week_bounds(TODAY)
        mock_gather.assert_called_once_with(USER_ID, expected_start, expected_end)

        # Verify Mon is actually a Monday and Sun is 6 days later
        from datetime import date as date_type

        mon = date_type.fromisoformat(expected_start)
        sun = date_type.fromisoformat(expected_end)
        assert mon.weekday() == 0, "week_start must be a Monday"
        assert sun.weekday() == 6, "week_end must be a Sunday"
        assert (sun - mon).days == 6, "Week must span exactly 7 days"

    @pytest.mark.asyncio
    async def test_response_shape(self):
        """Weekly review response contains all required fields."""
        mock_client = _fake_openai_client(
            summary="Good week overall",
            wins=["Hit targets 5/7 days"],
            focus=["Log every meal"],
            next_step="Weigh in every morning",
        )
        with (
            patch("api.services.coach_service.read_rows", return_value=[]),
            patch("api.services.coach_service.append_row"),
            patch("api.services.coach_service.get_async_client", return_value=mock_client),
            patch("api.services.coach_service._gather_weekly_context", return_value="ctx"),
        ):
            from api.services.coach_service import generate_weekly_review

            result = await generate_weekly_review(USER_ID, "UTC")

        assert isinstance(result.summary, str)
        assert isinstance(result.wins, list)
        assert isinstance(result.focus, list)
        assert isinstance(result.next_step, str)
        assert isinstance(result.week_start, str)
        assert isinstance(result.week_end, str)
        assert isinstance(result.generated_at, str)
        assert isinstance(result.cached, bool)
        # week_start must be a Monday
        from datetime import date as date_type
        assert date_type.fromisoformat(result.week_start).weekday() == 0


# ---------------------------------------------------------------------------
# Router tests
# ---------------------------------------------------------------------------


class TestGetCoachDailyEndpoint:
    def test_returns_200_with_coaching_shape(self, client, auth_headers):
        """GET /coach/daily → 200 with correct response keys."""
        fake_response = {
            "date": TODAY,
            "summary": "You did well today.",
            "wins": ["Hit protein"],
            "focus": ["Log weight"],
            "next_step": "Sleep 8h",
            "generated_at": _fresh_ts(),
            "cached": False,
        }
        with patch(
            "api.routers.coach.generate_daily_coaching",
            new=AsyncMock(return_value=MagicMock(**fake_response, model_dump=lambda: fake_response)),
        ):
            resp = client.get("/coach/daily", headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        for key in ("date", "summary", "wins", "focus", "next_step", "generated_at", "cached"):
            assert key in data, f"Missing key: {key}"

    def test_returns_401_without_auth(self, client):
        """GET /coach/daily without JWT → 401."""
        resp = client.get("/coach/daily")
        assert resp.status_code == 401

    def test_empty_state_no_data_does_not_500(self, client, auth_headers):
        """Service raising HTTPException → correct status code propagated to client."""
        from fastapi import HTTPException

        with patch(
            "api.routers.coach.generate_daily_coaching",
            new=AsyncMock(side_effect=HTTPException(status_code=503, detail="OpenAI unavailable")),
        ):
            resp = client.get("/coach/daily", headers=auth_headers)

        # HTTPException raised by the service should surface as 503, not crash as 500
        assert resp.status_code == 503


class TestGetCoachWeeklyEndpoint:
    def test_returns_200_with_weekly_shape(self, client, auth_headers):
        """GET /coach/weekly → 200 with week_start / week_end and coaching fields."""
        from api.services.coach_service import _current_week_bounds

        week_start, week_end = _current_week_bounds(TODAY)
        fake_response = {
            "week_start": week_start,
            "week_end": week_end,
            "summary": "Great week overall.",
            "wins": ["Consistent protein"],
            "focus": ["More sleep"],
            "next_step": "Plan meals Sunday",
            "generated_at": _fresh_ts(),
            "cached": False,
        }
        with patch(
            "api.routers.coach.generate_weekly_review",
            new=AsyncMock(return_value=MagicMock(**fake_response, model_dump=lambda: fake_response)),
        ):
            resp = client.get("/coach/weekly", headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        for key in ("week_start", "week_end", "summary", "wins", "focus", "next_step"):
            assert key in data, f"Missing key: {key}"

    def test_returns_401_without_auth(self, client):
        """GET /coach/weekly without JWT → 401."""
        resp = client.get("/coach/weekly")
        assert resp.status_code == 401
