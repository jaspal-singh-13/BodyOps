"""
Unit and integration tests for api/services/progress_service.py and
api/routers/progress.py (Phase 6 — Progress Analytics).

Service tests (mocked gspread + weight_service):
    TestGetProgressSummary
        - test_includes_weight_trend
        - test_7d_calorie_average_computed_correctly
        - test_7d_protein_average_computed_correctly
        - test_30d_workout_session_count
        - test_30d_mission_completion_rate
        - test_empty_meals_returns_zero_averages
        - test_no_weight_logs_returns_null_trend
        - test_user_id_scoping
        - test_outside_30d_sessions_excluded
        - test_projected_goal_date_propagated

Router tests:
    TestProgressSummaryEndpoint
        - test_returns_200_with_correct_shape
        - test_returns_401_without_auth
        - test_empty_data_returns_sensible_defaults
"""

import os
from datetime import date as date_type, datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import pytest

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-id")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")

USER_ID = 1
TODAY = datetime.now(timezone.utc).date().isoformat()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _day_offset(days: int) -> str:
    """Return a YYYY-MM-DD string ``days`` days before today."""
    return (date_type.fromisoformat(TODAY) - timedelta(days=days)).isoformat()


def _meal_row(user_id=USER_ID, date=TODAY, calories=500.0, protein=40.0):
    """Build a minimal Meals sheet row."""
    return {
        "user_id": str(user_id),
        "date": date,
        "total_calories": str(calories),
        "total_protein_g": str(protein),
    }


def _session_row(user_id=USER_ID, date=TODAY):
    """Build a minimal WorkoutSessions sheet row."""
    return {"user_id": str(user_id), "date": date}


def _status_row(user_id=USER_ID, date=TODAY, completed="FALSE"):
    """Build a minimal DailyTaskStatus sheet row."""
    return {"user_id": str(user_id), "date": date, "completed": completed}


def _null_trend():
    """Return a WeightTrendSummary with all-None values (used as default mock)."""
    from api.models.coach import WeightTrendSummary
    return WeightTrendSummary(total_loss_kg=None, projected_goal_date=None, seven_day_avg=None)


# ---------------------------------------------------------------------------
# TestGetProgressSummary — service unit tests
# ---------------------------------------------------------------------------


class TestGetProgressSummary:
    def test_includes_weight_trend(self):
        """Summary includes weight trend data derived from weight_service."""
        from api.models.coach import WeightTrendSummary

        with (
            patch("api.services.progress_service.read_rows", return_value=[]),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=WeightTrendSummary(
                    total_loss_kg=3.5,
                    projected_goal_date="2026-10-01",
                    seven_day_avg=84.5,
                ),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.weight_trend.total_loss_kg == 3.5
        assert result.weight_trend.projected_goal_date == "2026-10-01"

    def test_7d_calorie_average_computed_correctly(self):
        """7-day calorie average is the mean of daily totals in the window."""
        # 3 meals today — two 500 kcal + one 300 kcal = 1300 total for today
        # 1 meal yesterday — 700 kcal
        # Average over 2 days = (1300 + 700) / 2 = 1000
        meal_rows = [
            _meal_row(calories=500.0, protein=40.0, date=TODAY),
            _meal_row(calories=500.0, protein=30.0, date=TODAY),
            _meal_row(calories=300.0, protein=20.0, date=TODAY),
            _meal_row(calories=700.0, protein=50.0, date=_day_offset(1)),
        ]

        def _read(tab):
            return {"Meals": meal_rows, "WorkoutSessions": [], "DailyTaskStatus": []}.get(tab, [])

        with (
            patch("api.services.progress_service.read_rows", side_effect=_read),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=_null_trend(),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.calorie_avg_7d == 1000.0

    def test_7d_protein_average_computed_correctly(self):
        """7-day protein average is the mean of daily protein totals."""
        # Today: 40 + 30 = 70 g; yesterday: 50 g → avg = 60 g
        meal_rows = [
            _meal_row(calories=500.0, protein=40.0, date=TODAY),
            _meal_row(calories=400.0, protein=30.0, date=TODAY),
            _meal_row(calories=600.0, protein=50.0, date=_day_offset(1)),
        ]

        def _read(tab):
            return {"Meals": meal_rows, "WorkoutSessions": [], "DailyTaskStatus": []}.get(tab, [])

        with (
            patch("api.services.progress_service.read_rows", side_effect=_read),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=_null_trend(),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.protein_avg_7d == 60.0

    def test_30d_workout_session_count(self):
        """Sessions within 30-day window are counted correctly."""
        # 10 sessions in window, 2 older than 30 days → count = 10
        in_window = [_session_row(date=_day_offset(i)) for i in range(10)]
        outside = [_session_row(date=_day_offset(30 + i)) for i in range(2)]
        all_sessions = in_window + outside

        def _read(tab):
            return {"WorkoutSessions": all_sessions, "Meals": [], "DailyTaskStatus": []}.get(tab, [])

        with (
            patch("api.services.progress_service.read_rows", side_effect=_read),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=_null_trend(),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.workout_sessions_30d == 10

    def test_30d_mission_completion_rate(self):
        """Mission rate is completed/total * 100 within the 30-day window."""
        # 20 rows in window: 12 TRUE, 8 FALSE → rate = 60.0
        completed = [_status_row(date=_day_offset(i), completed="TRUE") for i in range(12)]
        pending = [_status_row(date=_day_offset(i + 12), completed="FALSE") for i in range(8)]
        all_status = completed + pending

        def _read(tab):
            return {
                "DailyTaskStatus": all_status,
                "WorkoutSessions": [],
                "Meals": [],
            }.get(tab, [])

        with (
            patch("api.services.progress_service.read_rows", side_effect=_read),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=_null_trend(),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.mission_rate_30d == 60.0

    def test_empty_meals_returns_zero_averages(self):
        """No meal rows → calorie_avg=0.0, protein_avg=0.0, no error raised."""
        with (
            patch("api.services.progress_service.read_rows", return_value=[]),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=_null_trend(),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.calorie_avg_7d == 0.0
        assert result.protein_avg_7d == 0.0

    def test_no_weight_logs_returns_null_trend(self):
        """Empty WeightLogs → trend fields are None, no exception raised."""
        from api.models.coach import WeightTrendSummary

        with (
            patch("api.services.progress_service.read_rows", return_value=[]),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=WeightTrendSummary(
                    total_loss_kg=None,
                    projected_goal_date=None,
                    seven_day_avg=None,
                ),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.weight_trend.total_loss_kg is None
        assert result.weight_trend.projected_goal_date is None
        assert result.weight_trend.seven_day_avg is None
        assert result.projected_goal_date is None

    def test_user_id_scoping(self):
        """Other users' rows are excluded from all aggregations."""
        other_meals = [_meal_row(user_id=2, calories=9999.0, protein=999.0)]
        other_sessions = [_session_row(user_id=2, date=TODAY)]
        other_status = [_status_row(user_id=2, completed="TRUE")]

        def _read(tab):
            return {
                "Meals": other_meals,
                "WorkoutSessions": other_sessions,
                "DailyTaskStatus": other_status,
            }.get(tab, [])

        with (
            patch("api.services.progress_service.read_rows", side_effect=_read),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=_null_trend(),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.calorie_avg_7d == 0.0
        assert result.protein_avg_7d == 0.0
        assert result.workout_sessions_30d == 0
        assert result.mission_rate_30d == 0.0

    def test_outside_30d_sessions_excluded(self):
        """Session dated 31 days ago is NOT counted."""
        old_session = _session_row(date=_day_offset(31))

        def _read(tab):
            return {"WorkoutSessions": [old_session], "Meals": [], "DailyTaskStatus": []}.get(tab, [])

        with (
            patch("api.services.progress_service.read_rows", side_effect=_read),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=_null_trend(),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.workout_sessions_30d == 0

    def test_projected_goal_date_propagated(self):
        """projected_goal_date from weight_trend appears as top-level field."""
        from api.models.coach import WeightTrendSummary

        with (
            patch("api.services.progress_service.read_rows", return_value=[]),
            patch(
                "api.services.progress_service._get_weight_trend",
                return_value=WeightTrendSummary(
                    total_loss_kg=4.0,
                    projected_goal_date="2026-11-15",
                    seven_day_avg=83.0,
                ),
            ),
        ):
            from api.services.progress_service import get_progress_summary

            result = get_progress_summary(USER_ID, "UTC")

        assert result.projected_goal_date == "2026-11-15"
        assert result.weight_trend.projected_goal_date == "2026-11-15"


# ---------------------------------------------------------------------------
# TestProgressSummaryEndpoint — router tests
# ---------------------------------------------------------------------------


class TestProgressSummaryEndpoint:
    def test_returns_200_with_correct_shape(self, client, auth_headers):
        """GET /progress/summary → 200 with all expected top-level keys."""
        fake = {
            "weight_trend": {
                "total_loss_kg": 3.0,
                "projected_goal_date": "2026-12-01",
                "seven_day_avg": 84.0,
            },
            "calorie_avg_7d": 1850.0,
            "protein_avg_7d": 145.0,
            "workout_sessions_30d": 12,
            "mission_rate_30d": 72.5,
            "projected_goal_date": "2026-12-01",
        }
        with patch(
            "api.routers.progress.get_progress_summary",
            return_value=MagicMock(**{k: v for k, v in fake.items()}, model_dump=lambda: fake),
        ):
            resp = client.get("/progress/summary", headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        for key in (
            "weight_trend",
            "calorie_avg_7d",
            "protein_avg_7d",
            "workout_sessions_30d",
            "mission_rate_30d",
            "projected_goal_date",
        ):
            assert key in data, f"Missing key: {key}"

    def test_returns_401_without_auth(self, client):
        """GET /progress/summary without JWT → 401."""
        resp = client.get("/progress/summary")
        assert resp.status_code == 401

    def test_empty_data_returns_sensible_defaults(self, client, auth_headers):
        """When all aggregations are empty → response still 200 with 0 / null values."""
        from api.models.coach import ProgressSummaryResponse, WeightTrendSummary

        empty = ProgressSummaryResponse(
            weight_trend=WeightTrendSummary(
                total_loss_kg=None,
                projected_goal_date=None,
                seven_day_avg=None,
            ),
            calorie_avg_7d=0.0,
            protein_avg_7d=0.0,
            workout_sessions_30d=0,
            mission_rate_30d=0.0,
            projected_goal_date=None,
        )
        with patch(
            "api.routers.progress.get_progress_summary",
            return_value=empty,
        ):
            resp = client.get("/progress/summary", headers=auth_headers)

        assert resp.status_code == 200
        data = resp.json()
        assert data["calorie_avg_7d"] == 0.0
        assert data["protein_avg_7d"] == 0.0
        assert data["workout_sessions_30d"] == 0
        assert data["mission_rate_30d"] == 0.0
        assert data["projected_goal_date"] is None
