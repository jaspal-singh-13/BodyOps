"""
Progress router — aggregated progress analytics.

Endpoints:
    GET /progress/summary — return a progress snapshot across all tracked metrics.

Requires a valid JWT.  The ``X-Timezone`` header scopes the date windows
(last 7 days for nutrition, last 30 days for sessions and missions) to the
user's local date rather than the server's UTC clock.
"""

import asyncio

from fastapi import APIRouter, Depends, Header

from ..auth import get_current_user
from ..logger import get_logger
from ..models.coach import ProgressSummaryResponse
from ..services.progress_service import get_progress_summary

logger = get_logger("routers.progress")

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/summary", response_model=ProgressSummaryResponse)
async def get_progress_summary_endpoint(
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> ProgressSummaryResponse:
    """
    Return a progress summary aggregating data from all tracking modules.

    Includes:
      - Weight trend (7-day MA, total loss, projected goal date)
      - 7-day calorie and protein averages
      - 30-day workout session count
      - 30-day mission completion rate

    All values degrade gracefully to 0 / ``null`` if data is absent, so this
    endpoint never returns 500 on a fresh account.

    Args:
        x_timezone: IANA timezone string for resolving date windows.

    Returns:
        ``ProgressSummaryResponse`` — always 200.
    """
    logger.info("GET /progress/summary user_id=%s tz=%s", user_id, x_timezone)
    return await asyncio.to_thread(get_progress_summary, user_id, x_timezone)
