"""
Pydantic models for the Workout System (Phase 3).

Request models:  WorkoutImportRequest, LogSetRequest, CompleteSessionRequest
Shared models:   ProgressionSuggestion, ExerciseInfo, WorkoutDaySummary
Response models: WorkoutImportResponse, TodayWorkoutResponse, TodayExercise,
                 LogSetResponse, ExerciseProgressionResponse, WorkoutHistoryResponse
"""

from __future__ import annotations

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared / nested
# ---------------------------------------------------------------------------


class ProgressionSuggestion(BaseModel):
    weight_kg: float | None
    reps: int | None
    note: str  # "first session" | "increase weight" | "add rep" | "reduce weight"


class ExerciseInfo(BaseModel):
    exercise_name: str
    sets: int
    rep_min: int
    rep_max: int
    order: int


class WorkoutDaySummary(BaseModel):
    day_name: str
    exercises: list[ExerciseInfo]


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class WorkoutImportRequest(BaseModel):
    plan_text: str
    schedule_text: str
    program_name: str


class AiWorkoutImportRequest(BaseModel):
    raw_text: str      # free-form workout text, any format
    program_name: str


class LogSetRequest(BaseModel):
    date: str
    exercise_name: str
    weight_kg: float
    reps: int
    day_name: str


class CompleteSessionRequest(BaseModel):
    date: str


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class WorkoutImportResponse(BaseModel):
    program_name: str
    program_days: int
    rest_days: int
    total_exercises: int
    days: list[WorkoutDaySummary]


class TodayExercise(BaseModel):
    exercise_name: str
    sets: int
    rep_min: int
    rep_max: int
    order: int
    last_weight_kg: float | None
    last_reps: int | None
    suggestion: ProgressionSuggestion
    sets_logged_today: int  # sets already logged in today's session (0 if none)


class TodayWorkoutResponse(BaseModel):
    date: str
    day_name: str
    is_rest_day: bool
    exercises: list[TodayExercise]
    estimated_duration_min: int  # sum(e.sets) * 2 + 5; 0 on rest day
    session_id: str | None  # None if no session started yet today
    is_completed: bool  # True once complete_session has been called
    plan_name: str | None = None


class LogSetResponse(BaseModel):
    session_id: str
    exercise_name: str
    set_number: int
    weight_kg: float
    reps: int
    logged_at: str
    suggestion: ProgressionSuggestion


class ExerciseProgressionResponse(BaseModel):
    exercise_name: str
    last_5_sessions: list[dict]
    suggestion: ProgressionSuggestion


class WorkoutHistoryResponse(BaseModel):
    sessions: list[dict]


class ScheduleDay(BaseModel):
    weekday: int          # 0=Mon … 6=Sun
    weekday_name: str     # "Monday" … "Sunday"
    day_name: str         # "Push", "Rest", etc.
    is_rest: bool
    exercises: list[ExerciseInfo]  # empty on rest days


class WorkoutScheduleResponse(BaseModel):
    program_name: str | None
    days: list[ScheduleDay]  # always 7, Mon–Sun order


class WorkoutPlanSummary(BaseModel):
    plan_id: str
    plan_name: str
    is_active: bool
    day_count: int
    exercise_count: int
    created_at: str


class WorkoutPlansResponse(BaseModel):
    plans: list[WorkoutPlanSummary]
