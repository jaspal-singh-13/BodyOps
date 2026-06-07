"""
Pydantic AI tool definitions for Phase 2 — Weight Tracking.

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
