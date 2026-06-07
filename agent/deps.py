import asyncio
from dataclasses import dataclass
from typing import Callable


@dataclass
class AgentDeps:
    user_id: int
    event_queue: asyncio.Queue
    # Service callables — injected by the API layer so this package stays isolated.
    weight_logger: Callable[[str, float], dict]   # (date, weight_kg) → serialised entry
    trend_getter: Callable[[], dict]              # () → serialised trend
