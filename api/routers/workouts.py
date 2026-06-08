"""
Workout system API routes.

Endpoints:
    POST   /workouts/import      — parse + import workout plan
    POST   /workouts/ai-import   — AI-powered import from free-form text
    GET    /workouts/today       — today's workout with progression suggestions
    POST   /workouts/log         — log a single set
    POST   /workouts/complete    — mark today's session complete
    GET    /workouts/progression — last 5 sessions for an exercise
    GET    /workouts/history     — all past sessions
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException

from ..auth import get_current_user
from ..models.workout import (
    AiWorkoutImportRequest,
    CompleteSessionRequest,
    ExerciseProgressionResponse,
    LogSetRequest,
    LogSetResponse,
    TodayWorkoutResponse,
    WorkoutHistoryResponse,
    WorkoutImportRequest,
    WorkoutImportResponse,
)
from ..services.workout_parser import WorkoutParseError, parse_workout_import
from ..services.workout_service import (
    ai_import_workout,
    complete_session,
    get_history,
    get_progression,
    get_today_workout,
    import_workout,
    log_set,
)

router = APIRouter(prefix="/workouts", tags=["workouts"])


@router.post("/ai-import", response_model=WorkoutImportResponse)
async def ai_import_endpoint(
    body: AiWorkoutImportRequest,
    user_id: int = Depends(get_current_user),
) -> WorkoutImportResponse:
    try:
        return await ai_import_workout(user_id, body.program_name, body.raw_text)
    except WorkoutParseError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.post("/import", response_model=WorkoutImportResponse)
async def import_workout_endpoint(
    body: WorkoutImportRequest,
    user_id: int = Depends(get_current_user),
) -> WorkoutImportResponse:
    try:
        days, schedule = parse_workout_import(body.plan_text, body.schedule_text)
    except WorkoutParseError as e:
        raise HTTPException(status_code=422, detail=str(e))
    return import_workout(user_id, body.program_name, days, schedule)


@router.get("/today", response_model=TodayWorkoutResponse)
async def get_today_endpoint(
    user_id: int = Depends(get_current_user),
) -> TodayWorkoutResponse:
    return get_today_workout(user_id, date.today().isoformat())


@router.post("/log", response_model=LogSetResponse)
async def log_set_endpoint(
    body: LogSetRequest,
    user_id: int = Depends(get_current_user),
) -> LogSetResponse:
    return log_set(user_id, body)


@router.post("/complete", status_code=204)
async def complete_session_endpoint(
    body: CompleteSessionRequest,
    user_id: int = Depends(get_current_user),
) -> None:
    complete_session(user_id, body.date)


@router.get("/progression", response_model=ExerciseProgressionResponse)
async def get_progression_endpoint(
    exercise: str,
    user_id: int = Depends(get_current_user),
) -> ExerciseProgressionResponse:
    return get_progression(user_id, exercise)


@router.get("/history", response_model=WorkoutHistoryResponse)
async def get_history_endpoint(
    user_id: int = Depends(get_current_user),
) -> WorkoutHistoryResponse:
    return get_history(user_id)
