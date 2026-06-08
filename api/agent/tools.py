"""
Pydantic AI tool definitions for Phases 2–4 (Weight, Workout, Meal Tracking).

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


# ---------------------------------------------------------------------------
# Phase 4 — Meal Tracking
# ---------------------------------------------------------------------------


@agent.tool
async def get_daily_nutrition(ctx: RunContext[AgentDeps]) -> dict:
    """
    Return today's consumed nutrition vs targets.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.

    Returns:
        Serialised ``DailyNutrition`` dict with consumed calories, protein,
        carbs, fat and their corresponding daily targets from Settings.
    """
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "get_daily_nutrition", "args": {}})
    result = ctx.deps.nutrition_getter()
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "get_daily_nutrition", "result": result})
    return result


@agent.tool
async def save_meal(
    ctx: RunContext[AgentDeps],
    meal_type: str,
    items: list[dict],
) -> dict:
    """
    Save a meal and its items to the Sheets.

    Use this when the user describes a meal in text (e.g. "had chicken, rice,
    and broccoli for lunch").  Items should be a list of dicts with at least
    ``name``, ``calories``, ``protein_g``, ``carbs_g``, ``fat_g`` fields.
    Quantity and confidence fields are optional.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.
        meal_type: One of "Breakfast", "Lunch", "Dinner", "Snack".
        items: List of food item dicts with macro estimates.

    Returns:
        Serialised ``SavedMealResponse`` with the meal ID and updated
        ``daily_nutrition`` totals.
    """
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "save_meal",
        "args": {"meal_type": meal_type, "items": items},
    })
    result = await ctx.deps.meal_saver(meal_type, items)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "save_meal", "result": result})
    return result


@agent.tool
async def analyze_meal_photo(ctx: RunContext[AgentDeps], image_url: str) -> dict:
    """
    Run AI vision analysis on a Drive-hosted meal photo URL.

    Returns a macro breakdown with detected food items.  The result is NOT
    automatically saved — call ``save_meal`` with the items to persist it.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.
        image_url: Publicly accessible URL of the meal photo (Google Drive
            ``uc?id=…`` URL, or any direct image URL).

    Returns:
        Serialised ``AnalyzeMealResponse`` with ``detected`` items and totals.
    """
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "analyze_meal_photo",
        "args": {"image_url": image_url},
    })
    result = await ctx.deps.meal_analyzer(image_url)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "analyze_meal_photo", "result": result})
    return result


@agent.tool
async def import_workout_from_text(
    ctx: RunContext[AgentDeps],
    raw_text: str,
    program_name: str,
) -> dict:
    """
    Import a workout plan from free-form text in any format.

    Uses AI to convert the text into the structured format, then saves it as
    the user's active workout program. Replaces any previously imported plan.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.
        raw_text: The workout plan in any free-form format.
        program_name: A name for the program (e.g. "PPL v2").

    Returns:
        Serialised ``WorkoutImportResponse`` dict with program/rest day counts
        and the list of imported days.
    """
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "import_workout_from_text",
        "args": {"program_name": program_name, "raw_text": raw_text},
    })
    result = await ctx.deps.workout_importer(raw_text, program_name)
    await ctx.deps.event_queue.put({
        "type": "tool_result",
        "tool": "import_workout_from_text",
        "result": result,
    })
    return result
