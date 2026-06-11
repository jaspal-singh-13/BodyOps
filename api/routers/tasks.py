"""
Tasks router — daily missions / task tracking.

Endpoints:
    GET  /tasks/today     — return today's task list (generates if missing).
    POST /tasks/complete  — mark a task complete by task_id + date.
    GET  /tasks/status    — today's summary (total, completed, percentage).

All endpoints require a valid JWT. Data is scoped to the authenticated user_id.
"""

import asyncio

from fastapi import APIRouter, Depends, Header

from ..auth import get_current_user
from ..models.task import CompleteTaskRequest, DailyStatusResponse
from ..services.task_service import complete_task, get_status, get_today_tasks

router = APIRouter(prefix="/tasks", tags=["tasks"])


@router.get("/today", response_model=DailyStatusResponse)
async def get_today_tasks_endpoint(
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> DailyStatusResponse:
    """
    Return today's mission list for the authenticated user.

    Generates the daily task rows if they don't exist yet (idempotent).
    The ``complete_workout`` task is omitted on rest days.

    Returns:
        ``DailyStatusResponse`` with task list and completion counts.
    """
    return await asyncio.to_thread(get_today_tasks, user_id, x_timezone)


@router.post("/complete", response_model=DailyStatusResponse)
async def complete_task_endpoint(
    body: CompleteTaskRequest,
    user_id: int = Depends(get_current_user),
) -> DailyStatusResponse:
    """
    Mark a task complete by its task_id and date.

    Idempotent — marking an already-complete task has no effect.

    Args:
        body: ``{task_id: str, date: YYYY-MM-DD}``

    Returns:
        Updated ``DailyStatusResponse`` for the given date.
    """
    return await asyncio.to_thread(complete_task, user_id, body.task_id, body.date)


@router.get("/status", response_model=DailyStatusResponse)
async def get_status_endpoint(
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> DailyStatusResponse:
    """
    Return today's mission summary (total, completed, percentage).

    Equivalent to ``GET /tasks/today`` — provided as a convenience alias.

    Returns:
        ``DailyStatusResponse`` with today's task list and counts.
    """
    return await asyncio.to_thread(get_status, user_id, x_timezone)
