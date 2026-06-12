"""
Coach router — daily and weekly AI coaching summaries.

Endpoints:
    GET /coach/daily   — return today's coaching (generate if absent or stale).
    GET /coach/weekly  — return this week's review (generate if absent).

Both endpoints require a valid JWT.  The ``X-Timezone`` header is forwarded to
the service layer so coaching is keyed on the user's local date rather than
the server's UTC clock.

Caching:
    - Daily:  served from ``CoachInsights`` if generated within the last 60 min.
    - Weekly: served from ``CoachInsights`` for the entire current ISO week.
"""

from fastapi import APIRouter, Depends, Header

from ..auth import get_current_user
from ..logger import get_logger
from ..models.coach import CoachingResponse, WeeklyReviewResponse
from ..services.coach_service import (
    generate_daily_coaching,
    generate_weekly_review,
)

logger = get_logger("routers.coach")

router = APIRouter(prefix="/coach", tags=["coach"])


@router.get("/daily", response_model=CoachingResponse)
async def get_daily_coaching(
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> CoachingResponse:
    """
    Return today's coaching summary, generating it if absent or stale.

    The first call each day (or after the 60-minute cache window) triggers
    an Azure OpenAI structured-output call and caches the result in the
    ``CoachInsights`` sheet.  Subsequent calls within the window return the
    cached result with ``cached=true`` in the response.

    Args:
        x_timezone: IANA timezone string for resolving "today" (e.g. "Asia/Kolkata").

    Returns:
        ``CoachingResponse`` with ``summary``, ``wins``, ``focus``, ``next_step``.
    """
    logger.info("GET /coach/daily user_id=%s tz=%s", user_id, x_timezone)
    return await generate_daily_coaching(user_id, x_timezone)


@router.get("/weekly", response_model=WeeklyReviewResponse)
async def get_weekly_review(
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> WeeklyReviewResponse:
    """
    Return this week's coaching review, generating it once per ISO week.

    Determines the current Mon–Sun week from ``X-Timezone``. If a weekly
    entry already exists in ``CoachInsights`` for that week, it is returned
    immediately.  Otherwise an OpenAI call is made, the result saved, and
    returned with ``cached=false``.

    Args:
        x_timezone: IANA timezone string for resolving the current week.

    Returns:
        ``WeeklyReviewResponse`` with ``week_start``, ``week_end``, coaching fields.
    """
    logger.info("GET /coach/weekly user_id=%s tz=%s", user_id, x_timezone)
    return await generate_weekly_review(user_id, x_timezone)
