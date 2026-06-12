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

import time

from pydantic_ai import RunContext

from ..logger import get_logger
from .agent import agent
from .deps import AgentDeps

logger = get_logger("agent.tools")


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
    logger.debug("tool=log_weight date=%s weight_kg=%s", date, weight_kg)
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "log_weight",
        "args": {"date": date, "weight_kg": weight_kg},
    })
    t0 = time.perf_counter()
    result = ctx.deps.weight_logger(date, weight_kg)
    logger.debug("tool=log_weight done (%.0f ms)", (time.perf_counter() - t0) * 1000)
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
    logger.debug("tool=get_weight_trend")
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "get_weight_trend", "args": {}})
    t0 = time.perf_counter()
    result = ctx.deps.trend_getter()
    logger.debug("tool=get_weight_trend done (%.0f ms)", (time.perf_counter() - t0) * 1000)
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
    logger.debug("tool=get_today_workout")
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "get_today_workout", "args": {}})
    t0 = time.perf_counter()
    result = ctx.deps.today_workout_getter()
    logger.debug("tool=get_today_workout done (%.0f ms)", (time.perf_counter() - t0) * 1000)
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
    logger.debug("tool=log_workout_set exercise=%s weight_kg=%s reps=%s", exercise_name, weight_kg, reps)
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "log_workout_set",
        "args": {"exercise_name": exercise_name, "weight_kg": weight_kg, "reps": reps},
    })
    t0 = time.perf_counter()
    result = ctx.deps.set_logger(exercise_name, weight_kg, reps)
    logger.debug("tool=log_workout_set done (%.0f ms)", (time.perf_counter() - t0) * 1000)
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
    logger.debug("tool=get_progression_target exercise=%s", exercise_name)
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "get_progression_target",
        "args": {"exercise_name": exercise_name},
    })
    t0 = time.perf_counter()
    result = ctx.deps.progression_getter(exercise_name)
    logger.debug("tool=get_progression_target done (%.0f ms)", (time.perf_counter() - t0) * 1000)
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
    logger.debug("tool=get_daily_nutrition")
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "get_daily_nutrition", "args": {}})
    t0 = time.perf_counter()
    result = ctx.deps.nutrition_getter()
    logger.debug("tool=get_daily_nutrition done (%.0f ms)", (time.perf_counter() - t0) * 1000)
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
    logger.debug("tool=save_meal meal_type=%s items=%d", meal_type, len(items))
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "save_meal",
        "args": {"meal_type": meal_type, "items": items},
    })
    t0 = time.perf_counter()
    result = await ctx.deps.meal_saver(meal_type, items)
    logger.debug("tool=save_meal done (%.0f ms)", (time.perf_counter() - t0) * 1000)
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
    logger.debug("tool=analyze_meal_photo url=%s", image_url)
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "analyze_meal_photo",
        "args": {"image_url": image_url},
    })
    t0 = time.perf_counter()
    result = await ctx.deps.meal_analyzer(image_url)
    logger.debug("tool=analyze_meal_photo done (%.0f ms)", (time.perf_counter() - t0) * 1000)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "analyze_meal_photo", "result": result})
    return result


# ---------------------------------------------------------------------------
# Phase 5 — Daily Missions
# ---------------------------------------------------------------------------


@agent.tool
async def get_task_status(ctx: RunContext[AgentDeps]) -> dict:
    """
    Return today's mission list with name, completion flag, and timestamp.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.

    Returns:
        Serialised ``DailyStatusResponse`` dict with ``date``, ``tasks``
        (each with ``name``, ``completed``, ``completed_at``), ``total``,
        ``completed`` count, and ``percentage``.
    """
    logger.debug("tool=get_task_status")
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "get_task_status", "args": {}})
    t0 = time.perf_counter()
    result = ctx.deps.task_status_getter()
    logger.debug("tool=get_task_status done (%.0f ms)", (time.perf_counter() - t0) * 1000)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "get_task_status", "result": result})
    return result


@agent.tool
async def complete_task(ctx: RunContext[AgentDeps], task_id: str) -> dict:
    """
    Mark a daily mission complete by its task ID.

    Use ``get_task_status`` first to find the correct ``task_id`` for the
    mission the user wants to complete.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.
        task_id: The ``id`` field from the task in ``get_task_status`` output.

    Returns:
        Updated ``DailyStatusResponse`` dict after marking the task complete.
    """
    logger.debug("tool=complete_task task_id=%s", task_id)
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "complete_task",
        "args": {"task_id": task_id},
    })
    t0 = time.perf_counter()
    result = ctx.deps.task_completer(task_id)
    logger.debug("tool=complete_task done (%.0f ms)", (time.perf_counter() - t0) * 1000)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "complete_task", "result": result})
    return result


# ---------------------------------------------------------------------------
# Phase 6 — AI Coach
# ---------------------------------------------------------------------------


@agent.tool
async def generate_daily_coaching(ctx: RunContext[AgentDeps]) -> dict:
    """
    Generate (or return cached) today's AI coaching summary.

    Gathers weight, nutrition, and mission data for the day, then calls
    Azure OpenAI to produce a structured coaching response. If coaching was
    already generated within the last 60 minutes, the cached result is returned
    without a new LLM call.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.

    Returns:
        ``CoachingResponse`` dict with ``summary``, ``wins``, ``focus``,
        ``next_step``, ``date``, ``generated_at``, and ``cached`` fields.
    """
    logger.debug("tool=generate_daily_coaching")
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "generate_daily_coaching", "args": {}})
    t0 = time.perf_counter()
    result = await ctx.deps.coaching_generator()
    logger.debug("tool=generate_daily_coaching done (%.0f ms)", (time.perf_counter() - t0) * 1000)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "generate_daily_coaching", "result": result})
    return result


@agent.tool
async def generate_weekly_review(ctx: RunContext[AgentDeps]) -> dict:
    """
    Generate (or return cached) the current week's AI coaching review.

    Covers the Mon–Sun ISO week containing today. Once generated for a given
    week, subsequent calls return the cached result without a new LLM call.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.

    Returns:
        ``WeeklyReviewResponse`` dict with ``summary``, ``wins``, ``focus``,
        ``next_step``, ``week_start``, ``week_end``, ``generated_at``, and
        ``cached`` fields.
    """
    logger.debug("tool=generate_weekly_review")
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "generate_weekly_review", "args": {}})
    t0 = time.perf_counter()
    result = await ctx.deps.weekly_review_generator()
    logger.debug("tool=generate_weekly_review done (%.0f ms)", (time.perf_counter() - t0) * 1000)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "generate_weekly_review", "result": result})
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
    a new plan in the user's plan library and makes it active. Previous plans
    are kept in the library and can be switched back to at any time.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.
        raw_text: The workout plan in any free-form format.
        program_name: A name for the new plan (e.g. "PPL v2", "Cut 3-day").
            If the user hasn't specified a name, derive one from the content.

    Returns:
        Serialised ``WorkoutImportResponse`` dict with program/rest day counts
        and the list of imported days.
    """
    logger.debug("tool=import_workout_from_text program=%r text_len=%d", program_name, len(raw_text))
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "import_workout_from_text",
        "args": {"program_name": program_name, "raw_text": raw_text},
    })
    t0 = time.perf_counter()
    result = await ctx.deps.workout_importer(raw_text, program_name)
    logger.debug("tool=import_workout_from_text done (%.0f ms)", (time.perf_counter() - t0) * 1000)
    await ctx.deps.event_queue.put({
        "type": "tool_result",
        "tool": "import_workout_from_text",
        "result": result,
    })
    return result


@agent.tool
async def list_workout_plans(ctx: RunContext[AgentDeps]) -> dict:
    """
    Return all saved workout plans in the user's plan library.

    Use this before switching plans so you know the exact plan names available.
    Each plan includes its name, whether it is currently active, and the number
    of workout days and exercises.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.

    Returns:
        Dict with a ``plans`` list, each item having ``plan_name``,
        ``is_active``, ``day_count``, and ``exercise_count``.
    """
    logger.debug("tool=list_workout_plans")
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "list_workout_plans", "args": {}})
    t0 = time.perf_counter()
    result = ctx.deps.plans_lister()
    logger.debug("tool=list_workout_plans done (%.0f ms)", (time.perf_counter() - t0) * 1000)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "list_workout_plans", "result": result})
    return result


@agent.tool
async def switch_workout_plan(ctx: RunContext[AgentDeps], plan_name: str) -> dict:
    """
    Switch the user's active workout plan by name.

    Resolves the name case-insensitively. The new plan takes effect immediately
    for today's workout and all future sessions. Any session already started
    today is not affected.

    Call ``list_workout_plans`` first if you are unsure of the exact plan name.
    On a name mismatch the tool returns an error dict with ``available_plans``
    so you can correct the name and retry.

    Args:
        ctx: Pydantic AI run context carrying ``AgentDeps``.
        plan_name: The name of the plan to activate (e.g. "PPL v2", "Cut 3-day").

    Returns:
        ``{"activated": True, "plan_name": "..."}`` on success, or
        ``{"error": "...", "available_plans": [...]}`` if not found.
    """
    logger.debug("tool=switch_workout_plan plan_name=%r", plan_name)
    await ctx.deps.event_queue.put({
        "type": "tool_call",
        "tool": "switch_workout_plan",
        "args": {"plan_name": plan_name},
    })
    t0 = time.perf_counter()
    result = ctx.deps.plan_switcher(plan_name)
    logger.debug("tool=switch_workout_plan done (%.0f ms)", (time.perf_counter() - t0) * 1000)
    await ctx.deps.event_queue.put({"type": "tool_result", "tool": "switch_workout_plan", "result": result})
    return result
