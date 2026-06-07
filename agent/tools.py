from pydantic_ai import RunContext

from .agent import agent
from .deps import AgentDeps


@agent.tool
async def log_weight(ctx: RunContext[AgentDeps], date: str, weight_kg: float) -> dict:
    """Log the user's weight for a given date (YYYY-MM-DD)."""
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
    """Get the user's weight trend: 7-day moving average and projected goal date."""
    await ctx.deps.event_queue.put({"type": "tool_call", "tool": "get_weight_trend", "args": {}})
    result = ctx.deps.trend_getter()
    await ctx.deps.event_queue.put({
        "type": "tool_result",
        "tool": "get_weight_trend",
        "result": result,
    })
    return result
