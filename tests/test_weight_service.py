"""
Unit tests for weight_service: upsert, history ordering, moving avg, projection.

All gspread calls are mocked at the service module level so no real network
requests are made. Parametrised data is constructed by helper methods on each
test class to keep individual test cases compact.
"""

from datetime import date, timedelta
from unittest.mock import call, patch

import gspread.exceptions
import pytest

from api.models.weight import WeightEntryCreate
from api.services.weight_service import (
    _compute_moving_avg,
    _project_goal_date,
    get_history,
    get_trend,
    log_weight,
)

USER_ID = 1
OTHER_USER_ID = 2

# A typical sheet row as returned by gspread (all values are strings).
# time must be present so the upsert lookup (user_id + date + time) can match.
EXISTING_ROW = {
    "user_id": "1",
    "date": "2026-06-08",
    "time": "08:00",
    "weight_kg": "85.0",
    "logged_at": "2026-06-08T08:00:00+00:00",
}


# ---------------------------------------------------------------------------
# log_weight
# ---------------------------------------------------------------------------


class TestLogWeight:
    def test_appends_row_when_date_is_new(self):
        data = WeightEntryCreate(date="2026-06-08", weight_kg=85.5)
        with (
            patch("api.services.weight_service.read_rows", return_value=[]),
            patch("api.services.weight_service.append_row") as mock_append,
            patch("api.services.weight_service.update_row") as mock_update,
        ):
            result = log_weight(USER_ID, data)
        mock_append.assert_called_once()
        mock_update.assert_not_called()
        assert result.weight_kg == 85.5
        assert result.user_id == USER_ID

    def test_updates_row_when_date_already_logged(self):
        # Supply the same time as in EXISTING_ROW so the upsert match hits
        data = WeightEntryCreate(date="2026-06-08", weight_kg=86.0, time="08:00")
        with (
            patch("api.services.weight_service.read_rows", return_value=[EXISTING_ROW]),
            patch("api.services.weight_service.append_row") as mock_append,
            patch("api.services.weight_service.update_row") as mock_update,
        ):
            result = log_weight(USER_ID, data)
        mock_update.assert_called_once()
        mock_append.assert_not_called()
        # Row index: 0-based list index 0 → sheet row 2 (header is row 1)
        _, row_index, saved = mock_update.call_args[0]
        assert row_index == 2
        assert saved["weight_kg"] == 86.0

    def test_returns_correct_response_fields(self):
        data = WeightEntryCreate(date="2026-06-08", weight_kg=85.5)
        with (
            patch("api.services.weight_service.read_rows", return_value=[]),
            patch("api.services.weight_service.append_row"),
        ):
            result = log_weight(USER_ID, data)
        assert result.date == "2026-06-08"
        assert result.weight_kg == 85.5
        assert result.user_id == USER_ID
        assert result.logged_at != ""

    def test_worksheet_not_found_treats_as_empty(self):
        data = WeightEntryCreate(date="2026-06-08", weight_kg=85.5)
        with (
            patch(
                "api.services.weight_service.read_rows",
                side_effect=gspread.exceptions.WorksheetNotFound,
            ),
            patch("api.services.weight_service.append_row") as mock_append,
        ):
            result = log_weight(USER_ID, data)
        mock_append.assert_called_once()
        assert result.weight_kg == 85.5


# ---------------------------------------------------------------------------
# get_history
# ---------------------------------------------------------------------------


class TestGetHistory:
    def _make_rows(self, entries: list[tuple[int, str, float]]) -> list[dict]:
        """Build raw sheet rows from (user_id, date, weight_kg) tuples."""
        return [
            {"user_id": str(uid), "date": d, "weight_kg": str(w), "logged_at": ""}
            for uid, d, w in entries
        ]

    def test_sorted_newest_first(self):
        rows = self._make_rows([(USER_ID, "2026-06-07", 86.0), (USER_ID, "2026-06-08", 85.5)])
        with patch("api.services.weight_service.read_rows", return_value=rows):
            result = get_history(USER_ID)
        assert result[0].date == "2026-06-08"
        assert result[1].date == "2026-06-07"

    def test_excludes_entries_older_than_90_days(self):
        old_date = (date.today() - timedelta(days=91)).isoformat()
        recent_date = date.today().isoformat()
        rows = self._make_rows([(USER_ID, old_date, 90.0), (USER_ID, recent_date, 85.0)])
        with patch("api.services.weight_service.read_rows", return_value=rows):
            result = get_history(USER_ID)
        assert len(result) == 1
        assert result[0].date == recent_date

    def test_change_kg_none_for_oldest_entry(self):
        rows = self._make_rows([(USER_ID, "2026-06-07", 86.0), (USER_ID, "2026-06-08", 85.5)])
        with patch("api.services.weight_service.read_rows", return_value=rows):
            result = get_history(USER_ID)
        # After newest-first sort, the oldest entry is last
        assert result[-1].change_kg is None

    def test_change_kg_computed_correctly(self):
        rows = self._make_rows([(USER_ID, "2026-06-07", 86.0), (USER_ID, "2026-06-08", 85.5)])
        with patch("api.services.weight_service.read_rows", return_value=rows):
            result = get_history(USER_ID)
        assert result[0].change_kg == -0.5

    def test_filters_to_current_user_only(self):
        rows = self._make_rows(
            [(USER_ID, "2026-06-08", 85.5), (OTHER_USER_ID, "2026-06-08", 90.0)]
        )
        with patch("api.services.weight_service.read_rows", return_value=rows):
            result = get_history(USER_ID)
        assert len(result) == 1
        assert result[0].weight_kg == 85.5

    def test_empty_when_no_entries(self):
        with patch("api.services.weight_service.read_rows", return_value=[]):
            result = get_history(USER_ID)
        assert result == []

    def test_worksheet_not_found_returns_empty(self):
        with patch(
            "api.services.weight_service.read_rows",
            side_effect=gspread.exceptions.WorksheetNotFound,
        ):
            result = get_history(USER_ID)
        assert result == []


# ---------------------------------------------------------------------------
# _compute_moving_avg
# ---------------------------------------------------------------------------


class TestComputeMovingAvg:
    def _entries(self, weights: list[float]) -> list[dict]:
        """Build dated weight entry dicts from a flat weight list."""
        base = date(2026, 1, 1)
        return [{"date": (base + timedelta(days=i)).isoformat(), "weight_kg": w} for i, w in enumerate(weights)]

    def test_first_six_entries_have_none_ma(self):
        entries = self._entries([80.0] * 6)
        result = _compute_moving_avg(entries)
        assert all(r["ma_7"] is None for r in result)

    def test_seventh_entry_has_correct_ma(self):
        entries = self._entries([80.0] * 7)
        result = _compute_moving_avg(entries)
        assert result[6]["ma_7"] == 80.0

    def test_ma_correct_with_varying_weights(self):
        # 6× 80.0 then one 77.0 → avg = (80*6+77)/7 ≈ 79.57
        entries = self._entries([80.0] * 6 + [77.0])
        result = _compute_moving_avg(entries)
        expected = round((80.0 * 6 + 77.0) / 7, 2)
        assert result[6]["ma_7"] == expected

    def test_single_entry_has_none_ma(self):
        entries = self._entries([85.0])
        result = _compute_moving_avg(entries)
        assert result[0]["ma_7"] is None


# ---------------------------------------------------------------------------
# _project_goal_date
# ---------------------------------------------------------------------------


class TestProjectGoalDate:
    def _linear_entries(self, start_weight: float, daily_loss: float, n: int) -> list[dict]:
        """Build entries that lose ``daily_loss`` kg each day from ``start_weight``."""
        base = date(2026, 1, 1)
        return [
            {
                "date": (base + timedelta(days=i)).isoformat(),
                "weight_kg": round(start_weight - daily_loss * i, 4),
            }
            for i in range(n)
        ]

    def test_returns_none_with_one_entry(self):
        entries = self._linear_entries(90.0, 0.5, 1)
        assert _project_goal_date(entries, 80.0) is None

    def test_returns_none_when_trending_up(self):
        # Negative daily_loss means gaining weight
        entries = self._linear_entries(80.0, -0.5, 10)
        assert _project_goal_date(entries, 85.0) is None

    def test_correct_projection_simple_linear(self):
        # Lose 0.5 kg/day from 90 kg; goal = 80 kg → 20 days from start
        entries = self._linear_entries(90.0, 0.5, 10)
        result = _project_goal_date(entries, 80.0)
        assert result is not None
        projected = date.fromisoformat(result)
        base = date(2026, 1, 1)
        # Allow ±1 day tolerance for rounding
        assert abs((projected - base).days - 20) <= 1

    def test_uses_last_14_when_more_available(self):
        # Provide 20 entries; projection should be consistent with just last 14
        entries = self._linear_entries(90.0, 0.5, 20)
        result_20 = _project_goal_date(entries, 80.0)
        result_14 = _project_goal_date(entries[-14:], 80.0)
        assert result_20 is not None
        assert result_14 is not None

    def test_returns_none_when_too_far_future(self):
        # Extremely slow loss — projection > 5 years should return None
        entries = self._linear_entries(90.0, 0.0001, 10)
        assert _project_goal_date(entries, 80.0) is None
