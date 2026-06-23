import asyncio

from fastapi import APIRouter, Depends, Header, HTTPException, status

from ..auth import get_current_user
from ..models.steps import StepsEntryCreate, StepsEntryResponse, StepsHistoryItem
from ..services.steps_service import delete_steps, get_history, log_steps

router = APIRouter(prefix="/steps", tags=["steps"])


@router.post("", response_model=StepsEntryResponse)
async def log_steps_endpoint(
    body: StepsEntryCreate,
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> StepsEntryResponse:
    return await asyncio.to_thread(log_steps, user_id, body, x_timezone)


@router.get("/history", response_model=list[StepsHistoryItem])
async def get_history_endpoint(
    user_id: int = Depends(get_current_user),
) -> list[StepsHistoryItem]:
    return await asyncio.to_thread(get_history, user_id)


@router.delete("/{date}/{time_str}", status_code=204)
async def delete_steps_endpoint(
    date: str,
    time_str: str,
    user_id: int = Depends(get_current_user),
) -> None:
    try:
        await asyncio.to_thread(delete_steps, user_id, date, time_str)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
