import asyncio
import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from agent import tools  # noqa: F401 — registers @agent.tool decorators
from agent.agent import agent
from agent.deps import AgentDeps
from agent.history import clear_all_sessions, get_session, update_session

from ..auth import get_current_user
from ..models.weight import WeightEntryCreate
from ..services.settings_service import get_settings
from ..services.weight_service import get_trend as svc_get_trend
from ..services.weight_service import log_weight as svc_log_weight

router = APIRouter(prefix="/agent", tags=["agent"])


class ChatRequest(BaseModel):
    message: str
    session_id: str


def _make_weight_logger(user_id: int):
    def weight_logger(date: str, weight_kg: float) -> dict:
        return svc_log_weight(user_id, WeightEntryCreate(date=date, weight_kg=weight_kg)).model_dump()
    return weight_logger


def _make_trend_getter(user_id: int):
    def trend_getter() -> dict:
        settings = get_settings(user_id)
        goal = settings.goal_weight_kg if settings else 0.0
        return svc_get_trend(user_id, goal).model_dump()
    return trend_getter


async def _run_agent_to_queue(
    message: str,
    history: list,
    deps: AgentDeps,
    session_id: str,
) -> None:
    try:
        async with agent.run_stream(message, message_history=history, deps=deps) as result:
            async for chunk in result.stream_text(delta=True):
                await deps.event_queue.put({"type": "text", "content": chunk})
            update_session(session_id, result.new_messages())
    except Exception as e:
        await deps.event_queue.put({"type": "error", "message": str(e)})
    finally:
        await deps.event_queue.put(None)


async def _sse_generator(message: str, session_id: str, user_id: int):
    queue: asyncio.Queue = asyncio.Queue()
    history = get_session(session_id)
    deps = AgentDeps(
        user_id=user_id,
        event_queue=queue,
        weight_logger=_make_weight_logger(user_id),
        trend_getter=_make_trend_getter(user_id),
    )

    task = asyncio.create_task(_run_agent_to_queue(message, history, deps, session_id))

    while True:
        event = await queue.get()
        if event is None:
            yield f"data: {json.dumps({'type': 'done'})}\n\n"
            break
        yield f"data: {json.dumps(event)}\n\n"

    await task


@router.post("/chat")
async def chat_endpoint(
    body: ChatRequest,
    user_id: int = Depends(get_current_user),
):
    return StreamingResponse(
        _sse_generator(body.message, body.session_id, user_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.delete("/history", status_code=204)
async def clear_history_endpoint(user_id: int = Depends(get_current_user)):
    clear_all_sessions()
