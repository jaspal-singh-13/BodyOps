"""
Pydantic models for AI Coach + Progress Analytics (Phase 6).

Data flow:
    GET /coach/daily    →                     → CoachingResponse
    GET /coach/weekly   →                     → WeeklyReviewResponse
    GET /progress/summary →                   → ProgressSummaryResponse
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Coach
# ---------------------------------------------------------------------------


class CoachingResponse(BaseModel):
    """
    Daily coaching summary returned by ``GET /coach/daily``.

    Attributes:
        date: The date this coaching is for (``YYYY-MM-DD``).
        summary: 1–2 sentence overview of the day's performance.
        wins: List of things the user did well today (may be empty).
        focus: List of areas to improve (may be empty).
        next_step: One concrete action the user should take.
        generated_at: ISO 8601 UTC timestamp of when the coaching was generated.
        cached: ``True`` if this response was served from the CoachInsights cache.
    """

    date: str
    summary: str
    wins: list[str]
    focus: list[str]
    next_step: str
    generated_at: str
    cached: bool = False


class WeeklyReviewResponse(BaseModel):
    """
    Weekly coaching review returned by ``GET /coach/weekly``.

    Attributes:
        week_start: ISO date of Monday for the reviewed week.
        week_end: ISO date of Sunday for the reviewed week.
        summary: 2–3 sentence overview of the week.
        wins: Standout wins from the week (may be empty).
        focus: Areas to work on next week (may be empty).
        next_step: One concrete priority for the upcoming week.
        generated_at: ISO 8601 UTC timestamp of when the review was generated.
        cached: ``True`` if this response was served from the CoachInsights cache.
    """

    week_start: str
    week_end: str
    summary: str
    wins: list[str]
    focus: list[str]
    next_step: str
    generated_at: str
    cached: bool = False


# ---------------------------------------------------------------------------
# Progress
# ---------------------------------------------------------------------------


class WeightTrendSummary(BaseModel):
    """
    Compact weight trend summary for the progress page.

    Attributes:
        total_loss_kg: Total weight lost since first log (positive = loss). ``None`` if < 2 entries.
        projected_goal_date: ISO date of projected goal-reach via linear regression. ``None`` if unavailable.
        seven_day_avg: Most recent 7-day moving average weight. ``None`` if < 7 entries.
    """

    total_loss_kg: Optional[float] = None
    projected_goal_date: Optional[str] = None
    seven_day_avg: Optional[float] = None


class ProgressSummaryResponse(BaseModel):
    """
    Progress analytics summary returned by ``GET /progress/summary``.

    Attributes:
        weight_trend: Compact weight trend with total loss and goal projection.
        calorie_avg_7d: Average daily calories over the last 7 days (0.0 if no data).
        protein_avg_7d: Average daily protein (g) over the last 7 days (0.0 if no data).
        workout_sessions_30d: Number of workout sessions logged in the last 30 days.
        mission_rate_30d: Mission completion rate over the last 30 days (0–100 %).
        projected_goal_date: Forwarded from ``weight_trend`` for convenient top-level access.
    """

    weight_trend: WeightTrendSummary
    calorie_avg_7d: float = 0.0
    protein_avg_7d: float = 0.0
    workout_sessions_30d: int = 0
    mission_rate_30d: float = 0.0
    projected_goal_date: Optional[str] = None
