"""
Pydantic AI tool definitions for Phases 2–3 (Weight Tracking + Workout System).

Each function decorated with ``@agent.tool`` is automatically registered on the
``agent`` instance (imported from ``agent.py``). Tools must be async and accept
a ``RunContext[AgentDeps]`` as their first argument.

Event protocol — every tool pushes two events to ``ctx.deps.event_queue`` so
the SSE stream shows activity in real time:

1. ``{"type": "tool_call",   "tool": <name>, "args": {...}}``  — before execution
2. ``{"type": "tool_result", "tool": <name>, "result": {...}}`` — after execution

The actual work is delegated to injected callables on ``AgentDeps`` so this
module has zero imports from ``api.*``.
"""

from pydantic_ai import RunContext

from .agent import agent
from .deps import AgentDeps


@agent.tool
async def log_weight(ctx: RunContext[AgentDeps], date: str, weight_kg: float) -> dict:
    """
    Log the user's body weight for a given date.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.
        date: Date of the weigh-in in ``YYYY-MM-DD`` format.
        weight_kg: Body weight in kilograms.

    Returns:
        Serialised ``WeightEntryResponse`` dict with ``date``, ``weight_kg``,
        ``user_id``, and ``logged_at`` fields.
    """
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "log_weight",
        "args": {"date": date, "weight_kg": weight_kg},
    })
    result = ctx.deps.weight_logger(date, weight_kg)
    await ctx.deps.event_queue.put({
        "type": "tool_result",
        "tool": "log_weight",
        "result": result,
    })
    return result


@agent.tool
async def get_weight_trend(ctx: RunContext[AgentDeps]) -> dict:
    """
    Retrieve the user's weight trend and goal projection.

    Fetches the 7-day moving average over all logged entries and a projected
    goal-reach date computed via linear regression on the last 14 weigh-ins.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.

    Returns:
        Serialised ``WeightTrendResponse`` dict with ``moving_avg`` (list of
        ``{date, weight_kg, ma_7}`` points), ``total_loss_kg``, and
        ``projected_goal_date`` (ISO string or ``null``).
    """
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "get_weight_trend", "args": {}})
    result = ctx.deps.trend_getter()
    await ctx.deps.event_queue.put({
        "type": "tool_result",
        "tool": "get_weight_trend",
        "result": result,
    })
    return result


# ---------------------------------------------------------------------------
# Phase 3 — Workout System
# ---------------------------------------------------------------------------


@agent.tool
async def get_today_workout(ctx: RunContext[AgentDeps]) -> dict:
    """
    Return today's workout plan with progressive overload suggestions.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.

    Returns:
        Serialised ``TodayWorkoutResponse`` dict including ``day_name``,
        ``is_rest_day``, and ``exercises`` with per-exercise suggestions.
    """
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "get_today_workout", "args": {}})
    result = ctx.deps.today_workout_getter()
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "get_today_workout", "result": result})
    return result


@agent.tool
async def log_workout_set(
    ctx: RunContext[AgentDeps],
    exercise_name: str,
    weight_kg: float,
    reps: int,
) -> dict:
    """
    Log a single set for a workout exercise.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.
        exercise_name: Name of the exercise (e.g. "Bench Press").
        weight_kg: Weight used in kilograms.
        reps: Number of reps completed.

    Returns:
        Serialised ``LogSetResponse`` dict with ``set_number``, ``logged_at``,
        and ``suggestion`` for the next set/session.
    """
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "log_workout_set",
        "args": {"exercise_name": exercise_name, "weight_kg": weight_kg, "reps": reps},
    })
    result = ctx.deps.set_logger(exercise_name, weight_kg, reps)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "log_workout_set", "result": result})
    return result


@agent.tool
async def get_progression_target(ctx: RunContext[AgentDeps], exercise_name: str) -> dict:
    """
    Return the suggested weight and reps for the next session of an exercise.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.
        exercise_name: Name of the exercise.

    Returns:
        Serialised ``ExerciseProgressionResponse`` dict with ``last_5_sessions``
        history and a ``suggestion`` (weight_kg, reps, note).
    """
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "get_progression_target",
        "args": {"exercise_name": exercise_name},
    })
    result = ctx.deps.progression_getter(exercise_name)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "get_progression_target", "result": result})
    return result
