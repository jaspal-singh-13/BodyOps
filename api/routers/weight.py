"""
Weight router — daily weigh-in logging and trend analytics.

Endpoints:
    POST   /weight                  — log (or update) a body weight entry for a given date.
    DELETE /weight/{date}/{time_str} — delete a specific weight entry.
    GET    /weight/history           — return the last 90 days of entries, newest first.
    GET    /weight/trend             — return 7-day moving average + projected goal date.

All endpoints require a valid JWT. Data is scoped to the authenticated user_id.
"""

import asyncio

from fastapi import APIRouter, Depends, Header, HTTPException, status

from ..auth import get_current_user
from ..models.weight import WeightEntryCreate, WeightEntryResponse, WeightHistoryItem, WeightTrendResponse
from ..services.settings_service import get_settings
from ..services.task_service import auto_complete_task
from ..services.weight_service import delete_weight, get_history, get_trend, log_weight

router = APIRouter(prefix="/weight", tags=["weight"])


async def _bg_auto_complete(user_id: int, task_type: str, date: str) -> None:
    """Fire-and-forget wrapper so task completion never delays the response."""
    try:
        await asyncio.to_thread(auto_complete_task, user_id, task_type, date)
    except Exception:
        pass


# Strong references to in-flight background tasks — asyncio only keeps weak
# references, so an unreferenced task can be garbage-collected before it runs.
_bg_tasks: set[asyncio.Task] = set()


def _spawn_bg(coro) -> None:
    """Run a coroutine as a background task that survives garbage collection."""
    task = asyncio.create_task(coro)
    _bg_tasks.add(task)
    task.add_done_callback(_bg_tasks.discard)


@router.post("", response_model=WeightEntryResponse)
async def log_weight_endpoint(
    body: WeightEntryCreate,
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> WeightEntryResponse:
    """
    Log a body weight entry, updating if an entry already exists for that date.

    The service layer performs an upsert: if a row with the same ``user_id``
    and ``date`` already exists in the ``WeightLogs`` tab, it is updated in
    place; otherwise a new row is appended.

    ``X-Timezone`` is used to derive the entry time when the client does not
    supply one, so the stored time reflects the user's local clock.

    Args:
        body: ``{date: YYYY-MM-DD, weight_kg: float}``

    Returns:
        The saved ``WeightEntryResponse`` including ``logged_at`` timestamp.
    """
    result = await asyncio.to_thread(log_weight, user_id, body, x_timezone)
    _spawn_bg(_bg_auto_complete(user_id, "log_weight", body.date))
    return result


@router.get("/history", response_model=list[WeightHistoryItem])
async def get_history_endpoint(
    user_id: int = Depends(get_current_user),
) -> list[WeightHistoryItem]:
    """
    Return the last 90 days of weight entries for the authenticated user.

    Entries are sorted newest-first. Each item includes a ``change_kg`` diff
    against the previous chronological entry (``None`` for the oldest entry).

    Returns:
        List of ``WeightHistoryItem`` objects; empty list if no entries exist.
    """
    return await asyncio.to_thread(get_history, user_id)


@router.get("/trend", response_model=WeightTrendResponse)
async def get_trend_endpoint(
    user_id: int = Depends(get_current_user),
) -> WeightTrendResponse:
    """
    Return 7-day moving average and linear-regression goal projection.

    Fetches ``goal_weight_kg`` from the user's settings to compute the
    projected goal-reach date. Returns 404 if settings don't exist yet
    (onboarding not complete).

    Returns:
        ``WeightTrendResponse`` with ``moving_avg``, ``total_loss_kg``,
        and ``projected_goal_date``.

    Raises:
        HTTPException(404): If no settings row exists for this user.
    """
    settings = await asyncio.to_thread(get_settings, user_id)
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No settings found")
    return await asyncio.to_thread(get_trend, user_id, settings.goal_weight_kg)


@router.delete("/{date}/{time_str}", status_code=204)
async def delete_weight_endpoint(
    date: str,
    time_str: str,
    user_id: int = Depends(get_current_user),
) -> None:
    """
    Delete a specific weight entry identified by date + time.

    Args:
        date: Date of the entry in ``YYYY-MM-DD`` format.
        time_str: Time of the entry in ``HH:MM`` format (colons encoded as ``%3A`` in URLs).

    Raises:
        HTTPException(404): If no matching entry is found for this user.
    """
    try:
        await asyncio.to_thread(delete_weight, user_id, date, time_str)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
