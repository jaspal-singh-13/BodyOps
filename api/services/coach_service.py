"""
AI coaching service for Phase 6 — AI Coach + Progress Analytics.

Generates daily and weekly coaching summaries using Azure OpenAI structured
output. Results are cached in the ``CoachInsights`` sheet to avoid redundant
LLM calls:

  - Daily:  cached for ``DAILY_CACHE_MINUTES`` (60 min). A second request within
            the window returns the cached row. A request after the window
            re-generates and updates the existing row in place.
  - Weekly: cached for the full week — once generated, any subsequent request
            for the same ISO week returns the cached result.

Data gathered before calling the LLM:
  - Settings (goal weight, targets)
  - Latest weight from WeightLogs
  - Today's nutrition totals from Meals + MealItems
  - Today's mission status from DailyTaskStatus

Tabs used:
    CoachInsights — one row per coaching entry (type="daily" or "weekly"),
                    scoped by user_id.
"""

from __future__ import annotations

import json
import os
import uuid
from datetime import date as date_type, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import gspread.exceptions
from pydantic import BaseModel

from ..agent.llm import get_async_client
from ..logger import get_logger
from ..models.coach import CoachingResponse, WeeklyReviewResponse
from ..sheets.sheets_repo import append_row, read_rows, to_int, update_row

logger = get_logger("coach_service")

COACH_TAB = "CoachInsights"
DAILY_CACHE_MINUTES = 60


# ---------------------------------------------------------------------------
# Internal structured-output schema (not exposed publicly)
# ---------------------------------------------------------------------------


class _CoachingSchema(BaseModel):
    summary: str
    wins: list[str]
    focus: list[str]
    next_step: str


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def generate_daily_coaching(user_id: int, tz_str: str = "UTC") -> CoachingResponse:
    """
    Return today's coaching summary, generating it if absent or stale.

    Caching behaviour:
      - If a ``type="daily"`` row exists for today AND was generated within
        the last ``DAILY_CACHE_MINUTES`` minutes → return cached, no LLM call.
      - If a row exists but is stale → regenerate and update the row in place.
      - If no row exists → generate fresh and append.

    Args:
        user_id: Authenticated user's integer ID.
        tz_str: IANA timezone string (e.g. "Asia/Kolkata") for resolving "today".

    Returns:
        ``CoachingResponse`` with ``cached=True`` when served from cache.
    """
    today = _resolve_today(tz_str)

    existing = _find_insight(user_id, "daily", today)
    if existing:
        generated_at_str = existing.get("generated_at", "")
        if generated_at_str and _is_fresh(generated_at_str, DAILY_CACHE_MINUTES):
            logger.info("Daily coaching cache hit user_id=%s date=%s", user_id, today)
            return _row_to_coaching(existing, cached=True)

    context = _gather_daily_context(user_id, today, tz_str)
    result = await _call_openai(context, "daily")
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "user_id": user_id,
        "id": existing.get("id", str(uuid.uuid4())) if existing else str(uuid.uuid4()),
        "date": today,
        "type": "daily",
        "summary": result.summary,
        "wins_json": json.dumps(result.wins),
        "focus_json": json.dumps(result.focus),
        "next_step": result.next_step,
        "generated_at": now,
    }

    if existing:
        _update_insight_row(existing["id"], row)
    else:
        append_row(COACH_TAB, row)

    logger.info("Daily coaching generated user_id=%s date=%s", user_id, today)
    return CoachingResponse(
        date=today,
        summary=result.summary,
        wins=result.wins,
        focus=result.focus,
        next_step=result.next_step,
        generated_at=now,
        cached=False,
    )


async def generate_weekly_review(user_id: int, tz_str: str = "UTC") -> WeeklyReviewResponse:
    """
    Return this week's coaching review, generating it if absent.

    Determines the current ISO week (Mon–Sun). Checks for an existing
    ``type="weekly"`` row keyed on ``week_start``. If found, returns it
    immediately without any LLM call. Otherwise gathers 7-day aggregated data,
    calls OpenAI, appends a new row, and returns.

    Args:
        user_id: Authenticated user's integer ID.
        tz_str: IANA timezone string for resolving the current week.

    Returns:
        ``WeeklyReviewResponse`` with ``cached=True`` when served from cache.
    """
    today = _resolve_today(tz_str)
    week_start, week_end = _current_week_bounds(today)

    existing = _find_insight(user_id, "weekly", week_start)
    if existing:
        logger.info("Weekly review cache hit user_id=%s week=%s", user_id, week_start)
        return _row_to_weekly(existing, week_start, week_end, cached=True)

    context = _gather_weekly_context(user_id, week_start, week_end)
    result = await _call_openai(context, "weekly")
    now = datetime.now(timezone.utc).isoformat()

    row = {
        "user_id": user_id,
        "id": str(uuid.uuid4()),
        "date": week_start,
        "type": "weekly",
        "summary": result.summary,
        "wins_json": json.dumps(result.wins),
        "focus_json": json.dumps(result.focus),
        "next_step": result.next_step,
        "generated_at": now,
    }
    append_row(COACH_TAB, row)

    logger.info("Weekly review generated user_id=%s week=%s", user_id, week_start)
    return WeeklyReviewResponse(
        week_start=week_start,
        week_end=week_end,
        summary=result.summary,
        wins=result.wins,
        focus=result.focus,
        next_step=result.next_step,
        generated_at=now,
        cached=False,
    )


# ---------------------------------------------------------------------------
# Sheet helpers
# ---------------------------------------------------------------------------


def _find_insight(user_id: int, insight_type: str, date: str) -> dict | None:
    """Return the first CoachInsights row matching user_id + type + date, or None."""
    try:
        rows = read_rows(COACH_TAB)
    except gspread.exceptions.WorksheetNotFound:
        return None
    for row in rows:
        if (
            to_int(row.get("user_id"), -1) == user_id
            and row.get("type") == insight_type
            and row.get("date") == date
        ):
            return row
    return None


def _update_insight_row(row_id: str, new_data: dict) -> None:
    """
    Update the CoachInsights row whose ``id`` matches ``row_id``.

    Reads all rows to find the 1-based sheet row index, then delegates to
    ``update_row``.  Silently logs and returns if the row cannot be found.
    """
    try:
        rows = read_rows(COACH_TAB)
        for i, row in enumerate(rows):
            if row.get("id") == row_id:
                update_row(COACH_TAB, i + 2, {**row, **new_data})
                return
        logger.warning("Coach insight row id=%s not found for update", row_id)
    except Exception:
        logger.exception("Failed to update coach insight id=%s", row_id)


def _row_to_coaching(row: dict, cached: bool = True) -> CoachingResponse:
    """Deserialise a CoachInsights row into a ``CoachingResponse``."""
    return CoachingResponse(
        date=row.get("date", ""),
        summary=row.get("summary", ""),
        wins=_parse_json_list(row.get("wins_json", "[]")),
        focus=_parse_json_list(row.get("focus_json", "[]")),
        next_step=row.get("next_step", ""),
        generated_at=row.get("generated_at", ""),
        cached=cached,
    )


def _row_to_weekly(
    row: dict,
    week_start: str,
    week_end: str,
    cached: bool = True,
) -> WeeklyReviewResponse:
    """Deserialise a CoachInsights row into a ``WeeklyReviewResponse``."""
    return WeeklyReviewResponse(
        week_start=week_start,
        week_end=week_end,
        summary=row.get("summary", ""),
        wins=_parse_json_list(row.get("wins_json", "[]")),
        focus=_parse_json_list(row.get("focus_json", "[]")),
        next_step=row.get("next_step", ""),
        generated_at=row.get("generated_at", ""),
        cached=cached,
    )


def _parse_json_list(val: str) -> list[str]:
    """Parse a JSON list string; return an empty list on any error."""
    try:
        result = json.loads(val)
        return result if isinstance(result, list) else []
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Date / time helpers
# ---------------------------------------------------------------------------


def _resolve_today(tz_str: str) -> str:
    """Return today's date as ``YYYY-MM-DD`` in the given timezone."""
    try:
        tz = ZoneInfo(tz_str)
        return datetime.now(tz).date().isoformat()
    except Exception:
        return date_type.today().isoformat()


def _current_week_bounds(today: str) -> tuple[str, str]:
    """
    Return (monday, sunday) ISO strings for the ISO week containing ``today``.

    Monday is ``weekday() == 0``, so subtracting weekday() days lands on Monday.
    """
    d = date_type.fromisoformat(today)
    monday = d - timedelta(days=d.weekday())
    sunday = monday + timedelta(days=6)
    return monday.isoformat(), sunday.isoformat()


def _is_fresh(generated_at_str: str, max_age_minutes: int) -> bool:
    """Return ``True`` if ``generated_at_str`` is within ``max_age_minutes`` of now."""
    try:
        generated_at = datetime.fromisoformat(generated_at_str)
        if generated_at.tzinfo is None:
            generated_at = generated_at.replace(tzinfo=timezone.utc)
        age_minutes = (datetime.now(timezone.utc) - generated_at).total_seconds() / 60
        return age_minutes < max_age_minutes
    except Exception:
        return False


# ---------------------------------------------------------------------------
# Data gathering
# ---------------------------------------------------------------------------


def _gather_daily_context(user_id: int, today: str, tz_str: str) -> str:
    """
    Gather today's fitness data as plain text for the daily coaching prompt.

    Imports services lazily to avoid circular imports. Each section degrades
    gracefully — if a service fails, a fallback line is appended instead.

    Args:
        user_id: Authenticated user's integer ID.
        today: Today's date string (``YYYY-MM-DD``).
        tz_str: IANA timezone string for resolving local dates.

    Returns:
        Multi-line string of context to inject into the LLM system prompt.
    """
    from ..services.settings_service import get_settings
    from ..services.weight_service import get_history as get_weight_history
    from ..services.meal_service import get_meals_today
    from ..services.task_service import get_today_tasks

    lines: list[str] = [f"Date: {today}"]

    # Settings — goal + targets
    settings = get_settings(user_id)
    if settings:
        lines.append(f"Name: {settings.name}")
        lines.append(f"Goal weight: {settings.goal_weight_kg} kg")
        lines.append(f"Calorie target: {settings.calorie_target} kcal/day")
        lines.append(f"Protein target: {settings.protein_target_g} g/day")

    # Weight
    try:
        history = get_weight_history(user_id)
        if history:
            lines.append(f"Latest weight: {history[0].weight_kg} kg (logged {history[0].date})")
            if settings and settings.goal_weight_kg:
                remaining = history[0].weight_kg - settings.goal_weight_kg
                lines.append(f"Remaining to goal: {remaining:.1f} kg")
        else:
            lines.append("Weight: no logs yet")
    except Exception:
        lines.append("Weight: unavailable")

    # Nutrition
    try:
        nutrition = get_meals_today(user_id, tz_str)
        lines.append(
            f"Calories today: {nutrition.calories} / {nutrition.target_calories} kcal"
        )
        lines.append(
            f"Protein today: {nutrition.protein_g:.0f} / {nutrition.target_protein_g:.0f} g"
        )
        lines.append(f"Meals logged: {nutrition.meals_count}")
    except Exception:
        lines.append("Nutrition: no data available")

    # Missions
    try:
        tasks = get_today_tasks(user_id, tz_str)
        lines.append(f"Missions: {tasks.completed}/{tasks.total} complete")
        for t in tasks.tasks:
            status = "done" if t.completed else "pending"
            lines.append(f"  [{status}] {t.name}")
    except Exception:
        lines.append("Missions: no data available")

    return "\n".join(lines)


def _gather_weekly_context(user_id: int, week_start: str, week_end: str) -> str:
    """
    Gather a week's aggregated data as plain text for the weekly review prompt.

    Args:
        user_id: Authenticated user's integer ID.
        week_start: Monday ISO date of the review week.
        week_end: Sunday ISO date of the review week.

    Returns:
        Multi-line string of context to inject into the LLM system prompt.
    """
    from ..services.settings_service import get_settings
    from ..services.weight_service import get_history as get_weight_history
    from ..services.meal_service import get_meals_history

    lines: list[str] = [f"Week: {week_start} to {week_end}"]

    settings = get_settings(user_id)
    if settings:
        lines.append(f"Name: {settings.name}")
        lines.append(f"Goal weight: {settings.goal_weight_kg} kg")
        lines.append(f"Calorie target: {settings.calorie_target} kcal/day")
        lines.append(f"Protein target: {settings.protein_target_g} g/day")

    # Weekly weight data
    try:
        history = get_weight_history(user_id)
        week_weights = [h for h in history if week_start <= h.date <= week_end]
        if week_weights:
            avg_w = sum(h.weight_kg for h in week_weights) / len(week_weights)
            lines.append(f"Weight logs this week: {len(week_weights)}")
            lines.append(f"Average weight: {avg_w:.1f} kg")
            lines.append(f"Latest weigh-in: {week_weights[0].weight_kg} kg")
        else:
            lines.append("Weight: no logs this week")
    except Exception:
        lines.append("Weight: unavailable")

    # Weekly nutrition
    try:
        meal_history = get_meals_history(user_id, days=7)
        week_days = [d for d in meal_history if week_start <= d.date <= week_end]
        if week_days:
            avg_cal = sum(d.total_calories for d in week_days) / len(week_days)
            avg_prot = sum(d.total_protein_g for d in week_days) / len(week_days)
            lines.append(f"Days with meals tracked: {len(week_days)}/7")
            lines.append(f"Avg calories: {avg_cal:.0f} kcal/day")
            lines.append(f"Avg protein: {avg_prot:.0f} g/day")
        else:
            lines.append("Nutrition: no meals logged this week")
    except Exception:
        lines.append("Nutrition: unavailable")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# LLM call
# ---------------------------------------------------------------------------

_DAILY_SYSTEM = """\
You are BodyOps, a supportive and data-driven fitness coach.
Given a summary of the user's activity today, generate a brief coaching response.

Return a JSON object with:
  • summary: 1-2 sentence overview of today's performance (be specific, use the numbers)
  • wins: list of 1-3 things the user did well today (strings, empty list if nothing to highlight)
  • focus: list of 1-2 areas to improve (strings, empty list if none)
  • next_step: one concrete action the user should take right now (string)

Be encouraging but honest. Prioritise nutrition and weight progress above all else.
"""

_WEEKLY_SYSTEM = """\
You are BodyOps, a supportive and data-driven fitness coach.
Given a summary of the user's activity this week, generate a weekly coaching review.

Return a JSON object with:
  • summary: 2-3 sentence overview of the week (be specific, use the numbers)
  • wins: list of 1-3 standout wins from the week (strings, empty list if none)
  • focus: list of 1-2 areas to work on next week (strings, empty list if none)
  • next_step: one concrete priority for the upcoming week (string)

Be encouraging but honest. Highlight trends and momentum.
"""


async def _call_openai(context: str, coaching_type: str) -> _CoachingSchema:
    """
    Call Azure OpenAI with structured output and return the parsed coaching schema.

    Args:
        context: Plain-text user context to include in the user message.
        coaching_type: ``"daily"`` or ``"weekly"`` — selects the system prompt.

    Returns:
        Parsed ``_CoachingSchema`` instance.

    Raises:
        ValueError: If OpenAI returns no parsed structured output.
    """
    system_prompt = _DAILY_SYSTEM if coaching_type == "daily" else _WEEKLY_SYSTEM
    client = get_async_client()
    completion = await client.beta.chat.completions.parse(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": context},
        ],
        response_format=_CoachingSchema,
    )
    msg = completion.choices[0].message
    if msg.parsed is None:
        raise ValueError("OpenAI returned no parsed coaching response")
    return msg.parsed
