"""
Workout system API routes.

Endpoints:
    POST   /workouts/import               — parse + import workout plan (new plan, non-destructive)
    POST   /workouts/ai-import            — AI-parse free-form workout text and import
    GET    /workouts/today                — today's workout with progression suggestions
    POST   /workouts/log                  — log a single set
    POST   /workouts/complete             — mark today's session complete
    GET    /workouts/progression          — last 5 sessions for an exercise
    GET    /workouts/history              — all past sessions
    GET    /workouts/schedule             — full Mon–Sun schedule with exercises
    GET    /workouts/plans                — list all saved plans
    POST   /workouts/plans/{plan_id}/activate         — switch active plan
    DELETE /workouts/plans/{plan_id}                  — delete a plan (active or not)
    PATCH  /workouts/plans/{plan_id}                  — rename a plan
    PUT    /workouts/plans/{plan_id}/days/{day_name}  — replace exercises for a day
    PATCH  /workouts/plans/{plan_id}/schedule/{weekday} — remap a weekday to a day type
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Header, HTTPException

from ..auth import get_current_user
from ..services.task_service import auto_complete_task
from ..models.workout import (
    AiWorkoutImportRequest,
    CompleteSessionRequest,
    ExerciseProgressionResponse,
    LogSetRequest,
    LogSetResponse,
    RenamePlanRequest,
    TodayWorkoutResponse,
    UpdateDayRequest,
    UpdateScheduleWeekdayRequest,
    WorkoutHistoryResponse,
    WorkoutImportRequest,
    WorkoutImportResponse,
    WorkoutPlansResponse,
    WorkoutScheduleResponse,
)
from ..services.workout_parser import WorkoutParseError, parse_workout_import
from ..services.workout_service import (
    activate_plan,
    ai_import_workout,
    complete_session,
    delete_plan,
    get_history,
    get_progression,
    get_schedule,
    get_today_workout,
    import_workout,
    list_plans,
    log_set,
    rename_plan,
    update_day_exercises,
    update_schedule_weekday,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


async def _bg_auto_complete(user_id: int, task_type: str, date: str) -> None:
    """Fire-and-forget wrapper so task completion never delays the response."""
    try:
        await asyncio.to_thread(auto_complete_task, user_id, task_type, date)
    except Exception:
        pass


@router.post("/import", response_model=WorkoutImportResponse)
async def import_workout_endpoint(
    body: WorkoutImportRequest,
    user_id: int = Depends(get_current_user),
) -> WorkoutImportResponse:
    try:
        days, schedule = parse_workout_import(body.plan_text, body.schedule_text)
    except WorkoutParseError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return await asyncio.to_thread(import_workout, user_id, body.program_name, days, schedule)


@router.post("/ai-import", response_model=WorkoutImportResponse)
async def ai_import_workout_endpoint(
    body: AiWorkoutImportRequest,
    user_id: int = Depends(get_current_user),
) -> WorkoutImportResponse:
    try:
        return await ai_import_workout(user_id, body.program_name, body.raw_text)
    except WorkoutParseError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/today", response_model=TodayWorkoutResponse)
async def get_today_endpoint(
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> TodayWorkoutResponse:
    from datetime import datetime
    from zoneinfo import ZoneInfo, ZoneInfoNotFoundError
    try:
        tz = ZoneInfo(x_timezone)
    except (ZoneInfoNotFoundError, KeyError):
        tz = ZoneInfo("UTC")
    today = datetime.now(tz).date().isoformat()
    return await asyncio.to_thread(get_today_workout, user_id, today)


@router.post("/log", response_model=LogSetResponse)
async def log_set_endpoint(
    body: LogSetRequest,
    user_id: int = Depends(get_current_user),
) -> LogSetResponse:
    return await asyncio.to_thread(log_set, user_id, body)


@router.post("/complete", status_code=204)
async def complete_session_endpoint(
    body: CompleteSessionRequest,
    user_id: int = Depends(get_current_user),
) -> None:
    await asyncio.to_thread(complete_session, user_id, body.date)
    asyncio.create_task(_bg_auto_complete(user_id, "complete_workout", body.date))


@router.get("/progression", response_model=ExerciseProgressionResponse)
async def get_progression_endpoint(
    exercise: str,
    user_id: int = Depends(get_current_user),
) -> ExerciseProgressionResponse:
    return await asyncio.to_thread(get_progression, user_id, exercise)


@router.get("/schedule", response_model=WorkoutScheduleResponse)
async def get_schedule_endpoint(
    user_id: int = Depends(get_current_user),
) -> WorkoutScheduleResponse:
    return await asyncio.to_thread(get_schedule, user_id)


@router.get("/history", response_model=WorkoutHistoryResponse)
async def get_history_endpoint(
    user_id: int = Depends(get_current_user),
) -> WorkoutHistoryResponse:
    return await asyncio.to_thread(get_history, user_id)


@router.get("/plans", response_model=WorkoutPlansResponse)
async def list_plans_endpoint(
    user_id: int = Depends(get_current_user),
) -> WorkoutPlansResponse:
    return await asyncio.to_thread(list_plans, user_id)


@router.post("/plans/{plan_id}/activate", status_code=204)
async def activate_plan_endpoint(
    plan_id: str,
    user_id: int = Depends(get_current_user),
) -> None:
    try:
        await asyncio.to_thread(activate_plan, user_id, plan_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.delete("/plans/{plan_id}", status_code=204)
async def delete_plan_endpoint(
    plan_id: str,
    user_id: int = Depends(get_current_user),
) -> None:
    try:
        await asyncio.to_thread(delete_plan, user_id, plan_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/plans/{plan_id}", status_code=204)
async def rename_plan_endpoint(
    plan_id: str,
    body: RenamePlanRequest,
    user_id: int = Depends(get_current_user),
) -> None:
    try:
        await asyncio.to_thread(rename_plan, user_id, plan_id, body.plan_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/plans/{plan_id}/days/{day_name}", status_code=204)
async def update_day_exercises_endpoint(
    plan_id: str,
    day_name: str,
    body: UpdateDayRequest,
    user_id: int = Depends(get_current_user),
) -> None:
    try:
        await asyncio.to_thread(update_day_exercises, user_id, plan_id, day_name, body.exercises)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/plans/{plan_id}/schedule/{weekday}", status_code=204)
async def update_schedule_weekday_endpoint(
    plan_id: str,
    weekday: int,
    body: UpdateScheduleWeekdayRequest,
    user_id: int = Depends(get_current_user),
) -> None:
    try:
        await asyncio.to_thread(update_schedule_weekday, user_id, plan_id, weekday, body.day_name)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
