"""
Progress analytics service for Phase 6 — AI Coach + Progress Analytics.

Aggregates data from multiple Google Sheets tabs to produce a single
``ProgressSummaryResponse`` that powers the ``/app/progress`` page.

Aggregated metrics:
  - Weight trend (7-day MA, total loss, projected goal date)
  - 7-day calorie average from the Meals tab (daily grouped)
  - 7-day protein average from the Meals tab
  - 30-day workout session count from WorkoutSessions
  - 30-day mission completion rate from DailyTaskStatus

All aggregations degrade gracefully — any missing data or sheet errors return
0 / ``None`` rather than raising, so the endpoint never 500s on sparse data.

Tabs used (read-only):
    Meals            — daily calorie/protein totals (7-day window)
    WorkoutSessions  — session rows (30-day window)
    DailyTaskStatus  — task completion rows (30-day window)
"""

from __future__ import annotations

from datetime import date as date_type, datetime, timedelta
from zoneinfo import ZoneInfo

import gspread.exceptions

from ..logger import get_logger
from ..models.coach import ProgressSummaryResponse, WeightTrendSummary
from ..sheets.sheets_repo import read_rows, to_float, to_int

logger = get_logger("progress_service")

MEALS_TAB = "Meals"
SESSIONS_TAB = "WorkoutSessions"
DAILY_STATUS_TAB = "DailyTaskStatus"


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def get_progress_summary(user_id: int, tz_str: str = "UTC") -> ProgressSummaryResponse:
    """
    Return a progress summary aggregating data from multiple sheet tabs.

    Calls weight service, then queries Meals, WorkoutSessions, and
    DailyTaskStatus directly.  All sub-computations are wrapped in
    try/except so a single failing tab never blocks the full response.

    Args:
        user_id: Authenticated user's integer ID.
        tz_str: IANA timezone string for resolving date windows.

    Returns:
        ``ProgressSummaryResponse`` — never raises, uses 0 / ``None`` for missing data.
    """
    today = _resolve_today(tz_str)

    weight_trend = _get_weight_trend(user_id)
    calorie_avg, protein_avg = _get_7d_nutrition_averages(user_id, today)
    sessions_30d = _get_30d_workout_sessions(user_id, today)
    mission_rate = _get_30d_mission_rate(user_id, today)

    return ProgressSummaryResponse(
        weight_trend=weight_trend,
        calorie_avg_7d=calorie_avg,
        protein_avg_7d=protein_avg,
        workout_sessions_30d=sessions_30d,
        mission_rate_30d=mission_rate,
        projected_goal_date=weight_trend.projected_goal_date,
    )


# ---------------------------------------------------------------------------
# Private sub-aggregations
# ---------------------------------------------------------------------------


def _resolve_today(tz_str: str) -> str:
    """Return today's date as ``YYYY-MM-DD`` in the given timezone."""
    try:
        tz = ZoneInfo(tz_str)
        return datetime.now(tz).date().isoformat()
    except Exception:
        return date_type.today().isoformat()


def _get_weight_trend(user_id: int) -> WeightTrendSummary:
    """
    Fetch weight trend for the user via ``weight_service``.

    Falls back to all-None summary if no settings row exists or the service
    raises for any reason.

    Returns:
        ``WeightTrendSummary`` with total_loss_kg, projected_goal_date, seven_day_avg.
    """
    from .weight_service import get_history as get_weight_history, get_trend
    from .settings_service import get_settings

    try:
        settings = get_settings(user_id)
        goal = settings.goal_weight_kg if settings else 0.0
        trend = get_trend(user_id, goal)

        avg_7d: float | None = None
        if trend.moving_avg:
            recent = [p["ma_7"] for p in trend.moving_avg if p.get("ma_7") is not None]
            if recent:
                avg_7d = recent[-1]

        return WeightTrendSummary(
            total_loss_kg=trend.total_loss_kg,
            projected_goal_date=trend.projected_goal_date,
            seven_day_avg=avg_7d,
        )
    except Exception:
        logger.exception("Failed to compute weight trend for user_id=%s", user_id)
        return WeightTrendSummary(
            total_loss_kg=None,
            projected_goal_date=None,
            seven_day_avg=None,
        )


def _get_7d_nutrition_averages(user_id: int, today: str) -> tuple[float, float]:
    """
    Return ``(calorie_avg, protein_avg)`` averaged over the last 7 days.

    Reads all rows from the ``Meals`` tab, filters to the 7-day window
    ``[today - 6 days, today]``, groups by date to get daily totals, then
    averages those daily totals.

    Args:
        user_id: Authenticated user's integer ID.
        today: Today's date string (``YYYY-MM-DD``).

    Returns:
        Tuple of ``(calorie_avg_7d, protein_avg_7d)`` rounded to 1 decimal.
        Both are ``0.0`` if no meal rows exist.
    """
    try:
        cutoff = (date_type.fromisoformat(today) - timedelta(days=6)).isoformat()
        rows = read_rows(MEALS_TAB)
        user_rows = [
            r for r in rows
            if to_int(r.get("user_id"), -1) == user_id
            and cutoff <= r.get("date", "") <= today
        ]
        if not user_rows:
            return 0.0, 0.0

        # Group by date: sum calories + protein per day
        by_date: dict[str, dict] = {}
        for r in user_rows:
            d = r.get("date", "")
            entry = by_date.setdefault(d, {"calories": 0.0, "protein": 0.0})
            entry["calories"] += to_float(r.get("total_calories"), 0.0)
            entry["protein"] += to_float(r.get("total_protein_g"), 0.0)

        days = list(by_date.values())
        calorie_avg = sum(d["calories"] for d in days) / len(days)
        protein_avg = sum(d["protein"] for d in days) / len(days)
        return round(calorie_avg, 1), round(protein_avg, 1)

    except gspread.exceptions.WorksheetNotFound:
        return 0.0, 0.0
    except Exception:
        logger.exception("Failed to compute nutrition averages for user_id=%s", user_id)
        return 0.0, 0.0


def _get_30d_workout_sessions(user_id: int, today: str) -> int:
    """
    Count WorkoutSessions rows for the user in the last 30 days.

    A session is counted regardless of whether it was ``completed`` — the
    presence of a row in ``WorkoutSessions`` means the user started a session.

    Args:
        user_id: Authenticated user's integer ID.
        today: Today's date string (``YYYY-MM-DD``).

    Returns:
        Integer count of sessions in the window; 0 if none or sheet missing.
    """
    try:
        cutoff = (date_type.fromisoformat(today) - timedelta(days=29)).isoformat()
        rows = read_rows(SESSIONS_TAB)
        return sum(
            1 for r in rows
            if to_int(r.get("user_id"), -1) == user_id
            and cutoff <= r.get("date", "") <= today
        )
    except gspread.exceptions.WorksheetNotFound:
        return 0
    except Exception:
        logger.exception("Failed to count workout sessions for user_id=%s", user_id)
        return 0


def _get_30d_mission_rate(user_id: int, today: str) -> float:
    """
    Return mission completion rate (0–100 %) over the last 30 days.

    Reads ``DailyTaskStatus`` rows for the user in the 30-day window and
    computes ``completed_count / total_count * 100``.

    Args:
        user_id: Authenticated user's integer ID.
        today: Today's date string (``YYYY-MM-DD``).

    Returns:
        Float percentage rounded to 1 decimal; 0.0 if no task rows exist.
    """
    try:
        cutoff = (date_type.fromisoformat(today) - timedelta(days=29)).isoformat()
        rows = read_rows(DAILY_STATUS_TAB)
        user_rows = [
            r for r in rows
            if to_int(r.get("user_id"), -1) == user_id
            and cutoff <= r.get("date", "") <= today
        ]
        total = len(user_rows)
        if total == 0:
            return 0.0
        completed = sum(1 for r in user_rows if r.get("completed") == "TRUE")
        return round(completed / total * 100, 1)
    except gspread.exceptions.WorksheetNotFound:
        return 0.0
    except Exception:
        logger.exception("Failed to compute mission rate for user_id=%s", user_id)
        return 0.0
