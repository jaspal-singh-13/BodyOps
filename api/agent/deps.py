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
        weight_logger: Callable that logs a weight entry for the user. Signature:
            ``(date: str, weight_kg: float) -> dict`` where ``date`` is
            ``YYYY-MM-DD``. Returns the serialised ``WeightEntryResponse``.
        trend_getter: Callable that returns the user's weight trend. Signature:
            ``() -> dict``. Returns the serialised ``WeightTrendResponse``
            including 7-day moving average and projected goal date.
    """

    user_id: int
    event_queue: asyncio.Queue
    weight_logger: Callable[[str, float], dict]
    trend_getter: Callable[[], dict]
