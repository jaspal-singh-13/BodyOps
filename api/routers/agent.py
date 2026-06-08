"""
Agent router — SSE-streaming AI coach chat.

Endpoints:
    POST   /agent/chat     — run the Pydantic AI agent and stream events via SSE.
    DELETE /agent/history  — clear all in-memory session history.

Architecture
------------
The SSE pipeline uses a shared ``asyncio.Queue`` to decouple the agent
background task from the streaming generator:

    Browser ──SSE──► /agent/chat ──► _sse_generator
                                          │
                              asyncio.Queue (shared)
                                          │
                           _run_agent_to_queue (background task)
                                          │
                                   agent.run_stream()
                                          │
                                tools (emit events to queue)

This design means tool_call / tool_result events appear in the client's
stream in real time, before the final text reply is assembled.

Dependency injection
--------------------
Closure factories capture ``user_id`` and delegate to service functions.
These callables are injected into ``AgentDeps`` so the top-level ``agent``
package remains free of any ``api.*`` imports.
"""

import asyncio
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

# noqa: F401 — importing tools triggers @agent.tool decorator registration
from ..agent import tools  # noqa: F401
from ..agent.agent import agent
from ..agent.deps import AgentDeps
from ..agent.history import clear_all_sessions, get_session, update_session

from ..auth import get_current_user
from ..models.weight import WeightEntryCreate
from ..models.workout import LogSetRequest
from ..services.settings_service import get_settings
from ..services.weight_service import get_trend as svc_get_trend
from ..services.weight_service import log_weight as svc_log_weight
from ..services.meal_service import get_meals_today as svc_get_meals_today
from ..services.meal_service import save_meal as svc_save_meal
from ..services.meal_vision import analyze_meal as svc_analyze_meal
from ..models.meal import ConfirmMealRequest, DetectedItem
from ..services.workout_service import ai_import_workout as svc_ai_import_workout
from ..services.workout_service import get_progression as svc_get_progression
from ..services.workout_service import get_today_workout as svc_get_today_workout
from ..services.workout_service import log_set as svc_log_set

router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    """Request body for ``POST /agent/chat``."""

    message: str
    session_id: str  # client-generated UUID; used to look up conversation history


def _make_weight_logger(user_id: int):
    """
    Return a callable that logs a weight entry for the given user.

    The returned closure matches the ``weight_logger`` signature expected by
    ``AgentDeps``: ``(date: str, weight_kg: float) -> dict``.

    Args:
        user_id: Authenticated user's integer ID to scope the write.

    Returns:
        Callable that delegates to ``svc_log_weight`` and serialises the result.
    """
    def weight_logger(date: str, weight_kg: float) -> dict:
        return svc_log_weight(user_id, WeightEntryCreate(date=date, weight_kg=weight_kg)).model_dump()
    return weight_logger


def _make_trend_getter(user_id: int):
    """
    Return a callable that fetches the weight trend for the given user.

    Falls back to ``goal_weight_kg=0.0`` if the user has no settings row yet
    (trend will still be computed, just without a meaningful projection).

    The returned closure matches the ``trend_getter`` signature expected by
    ``AgentDeps``: ``() -> dict``.

    Args:
        user_id: Authenticated user's integer ID to scope the read.

    Returns:
        Callable that delegates to ``svc_get_trend`` and serialises the result.
    """
    def trend_getter() -> dict:
        settings = get_settings(user_id)
        goal = settings.goal_weight_kg if settings else 0.0
        return svc_get_trend(user_id, goal).model_dump()
    return trend_getter


def _make_today_workout_getter(user_id: int):
    """Return a callable that fetches today's workout for the given user."""
    from datetime import date as _date

    def today_workout_getter() -> dict:
        return svc_get_today_workout(user_id, _date.today().isoformat()).model_dump()
    return today_workout_getter


def _make_set_logger(user_id: int):
    """Return a callable that logs a workout set for the given user."""
    from datetime import date as _date

    def set_logger(exercise_name: str, weight_kg: float, reps: int) -> dict:
        today = _date.today().isoformat()
        today_workout = svc_get_today_workout(user_id, today)
        day_name = today_workout.day_name
        req = LogSetRequest(
            date=today,
            exercise_name=exercise_name,
            weight_kg=weight_kg,
            reps=reps,
            day_name=day_name,
        )
        return svc_log_set(user_id, req).model_dump()
    return set_logger


def _make_progression_getter(user_id: int):
    """Return a callable that fetches progression data for an exercise."""
    def progression_getter(exercise_name: str) -> dict:
        return svc_get_progression(user_id, exercise_name).model_dump()
    return progression_getter


def _make_workout_importer(user_id: int):
    """Return an async callable that AI-imports a workout from free-form text."""
    async def workout_importer(raw_text: str, program_name: str) -> dict:
        return (await svc_ai_import_workout(user_id, program_name, raw_text)).model_dump()
    return workout_importer


def _make_nutrition_getter(user_id: int):
    """Return a callable that fetches today's nutrition totals for the user."""
    def nutrition_getter() -> dict:
        return svc_get_meals_today(user_id, "UTC").model_dump()
    return nutrition_getter


def _make_meal_saver(user_id: int):
    """Return an async callable that saves a meal from free-form item dicts."""
    from datetime import date as _date

    async def meal_saver(meal_type: str, items: list[dict]) -> dict:
        detected = [
            DetectedItem(
                name=it.get("name", "Unknown"),
                quantity=it.get("quantity", ""),
                calories=int(it.get("calories", 0)),
                protein_g=float(it.get("protein_g", 0)),
                carbs_g=float(it.get("carbs_g", 0)),
                fat_g=float(it.get("fat_g", 0)),
                confidence=it.get("confidence", "med"),  # type: ignore[arg-type]
            )
            for it in items
        ]
        req = ConfirmMealRequest(
            meal_type=meal_type,  # type: ignore[arg-type]
            items=detected,
            drive_url="",
            date=_date.today().isoformat(),
        )
        import asyncio as _asyncio
        return (await _asyncio.to_thread(svc_save_meal, user_id, req, "UTC")).model_dump()
    return meal_saver


def _make_meal_analyzer(user_id: int):  # noqa: ARG001 — user_id reserved for future scoping
    """Return an async callable that runs vision analysis on a meal photo URL."""
    async def meal_analyzer(image_url: str) -> dict:
        result = await svc_analyze_meal(image_url, image_url)
        return result.model_dump()
    return meal_analyzer


async def _run_agent_to_queue(
    message: str,
    history: list,
    deps: AgentDeps,
    session_id: str,
) -> None:
    """
    Run the Pydantic AI agent in a background task, pushing all events to the queue.

    Streams text deltas from ``result.stream_text(delta=True)`` as
    ``{"type": "text", "content": chunk}`` events. Tools push their own
    ``tool_call`` / ``tool_result`` events directly to the queue.

    Sends ``None`` as a sentinel when the stream is fully consumed (or on error)
    so the SSE generator knows to close the connection.

    Args:
        message: The user's latest message.
        history: Prior ``ModelMessage`` objects for this session (multi-turn context).
        deps: Injected ``AgentDeps`` containing the queue and service callables.
        session_id: Session ID used to persist new messages to history store.
    """
    try:
        async with agent.run_stream(message, message_history=history, deps=deps) as result:
            async for chunk in result.stream_text(delta=True):
                await deps.event_queue.put({"type": "text", "content": chunk})
            # Persist the full exchange so future turns have context
            update_session(session_id, result.new_messages())
    except Exception as e:
        await deps.event_queue.put({"type": "error", "message": str(e)})
    finally:
        # Sentinel: tells _sse_generator the stream is finished
        await deps.event_queue.put(None)


async def _sse_generator(message: str, session_id: str, user_id: int):
    """
    Async generator that yields SSE-formatted event strings.

    Creates the shared queue, builds ``AgentDeps`` with injected service
    callables, launches ``_run_agent_to_queue`` as a background task, then
    drains the queue yielding one SSE line per event.

    The generator closes (and awaits the background task) when it receives
    the ``None`` sentinel, which triggers a ``{"type": "done"}`` event.

    Args:
        message: User's latest message text.
        session_id: Client-generated UUID for session continuity.
        user_id: Authenticated user's integer ID.

    Yields:
        SSE-formatted strings: ``data: {json}\n\n``
    """
    queue: asyncio.Queue = asyncio.Queue()
    history = get_session(session_id)
    deps = AgentDeps(
        user_id=user_id,
        event_queue=queue,
        weight_logger=_make_weight_logger(user_id),
        trend_getter=_make_trend_getter(user_id),
        today_workout_getter=_make_today_workout_getter(user_id),
        set_logger=_make_set_logger(user_id),
        progression_getter=_make_progression_getter(user_id),
        workout_importer=_make_workout_importer(user_id),
        nutrition_getter=_make_nutrition_getter(user_id),
        meal_saver=_make_meal_saver(user_id),
        meal_analyzer=_make_meal_analyzer(user_id),
    )

    # Run agent in background so this generator can yield events as they arrive
    task = asyncio.create_task(_run_agent_to_queue(message, history, deps, session_id))

    while True:
        event = await queue.get()
        if event is None:
            # Sentinel received — stream is complete
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            break
        yield f"data: {json.dumps(event)}\n\n"

    # Ensure background task is fully cleaned up before the response closes
    await task


@router.post("/chat")
async def chat_endpoint(
    body: ChatRequest,
    user_id: int = Depends(get_current_user),
):
    """
    Stream an AI coach response as Server-Sent Events.

    Returns a ``text/event-stream`` response. Each event is a newline-delimited
    JSON object with a ``type`` field:

    - ``{"type": "tool_call",   "tool": "...", "args": {...}}``
    - ``{"type": "tool_result", "tool": "...", "result": {...}}``
    - ``{"type": "text",        "content": "..."}``
    - ``{"type": "done"}``
    - ``{"type": "error",       "message": "..."}``

    The ``Cache-Control: no-cache`` and ``X-Accel-Buffering: no`` headers
    prevent proxies (nginx, Vercel) from buffering the stream.
    """
    return StreamingResponse(
        _sse_generator(body.message, body.session_id, user_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.delete("/history", status_code=204)
async def clear_history_endpoint(user_id: int = Depends(get_current_user)):
    """
    Clear all in-memory conversation history for all sessions.

    Useful for debugging or when the user explicitly wants to start fresh.
    Note: clears history for ALL sessions in the process, not just the
    authenticated user's — acceptable for a single-user app.

    Returns:
        HTTP 204 No Content on success.
    """
    clear_all_sessions()
