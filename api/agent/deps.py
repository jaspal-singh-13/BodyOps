"""
Runtime dependencies injected into every agent tool call.

This module is intentionally free of any ``api.*`` imports. The API layer
constructs an ``AgentDeps`` instance and passes service logic in as plain
callables, keeping the ``agent`` package fully decoupled from FastAPI and the
Google Sheets service layer.
"""

import asyncio
from dataclasses import dataclass
from typing import Callable


@dataclass
class AgentDeps:
    """
    Dependency container passed to every Pydantic AI tool via ``RunContext.deps``.

    Attributes:
        user_id: Authenticated user's integer ID, scopes all data operations.
        event_queue: Async queue shared between the agent background task and the
            SSE generator. Tools push ``tool_call`` / ``tool_result`` dicts here
            so the client sees events in real time before the final text reply.
        weight_logger: ``(date, weight_kg) -> dict`` — log a weight entry.
        trend_getter: ``() -> dict`` — return weight trend + projected goal date.
        today_workout_getter: ``() -> dict`` — return today's workout with suggestions.
        set_logger: ``(exercise_name, weight_kg, reps) -> dict`` — log a single set.
        progression_getter: ``(exercise_name) -> dict`` — return last 5 sessions + suggestion.
        workout_importer: ``async (raw_text, program_name) -> dict`` — AI-import a workout from free-form text.
        nutrition_getter: ``() -> dict`` — return today's nutrition totals vs targets.
        meal_saver: ``async (meal_type, items) -> dict`` — save a confirmed meal.
        meal_analyzer: ``async (image_url) -> dict`` — run vision analysis on a meal photo.
    """

    user_id: int
    event_queue: asyncio.Queue
    weight_logger: Callable[[str, float], dict]
    trend_getter: Callable[[], dict]
    today_workout_getter: Callable[[], dict]
    set_logger: Callable[[str, float, int], dict]
    progression_getter: Callable[[str], dict]
    workout_importer: Callable[[str, str], dict]
    nutrition_getter: Callable[[], dict]
    meal_saver: Callable[..., dict]
    meal_analyzer: Callable[[str], dict]
