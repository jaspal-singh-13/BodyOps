from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import get_current_user
from ..models.weight import WeightEntryCreate, WeightEntryResponse, WeightHistoryItem, WeightTrendResponse
from ..services.settings_service import get_settings
from ..services.weight_service import get_history, get_trend, log_weight

router = APIRouter(prefix="/weight", tags=["weight"])


@router.post("", response_model=WeightEntryResponse)
async def log_weight_endpoint(
    body: WeightEntryCreate,
    user_id: int = Depends(get_current_user),
) -> WeightEntryResponse:
    return log_weight(user_id, body)


@router.get("/history", response_model=list[WeightHistoryItem])
async def get_history_endpoint(
    user_id: int = Depends(get_current_user),
) -> list[WeightHistoryItem]:
    return get_history(user_id)


@router.get("/trend", response_model=WeightTrendResponse)
async def get_trend_endpoint(
    user_id: int = Depends(get_current_user),
) -> WeightTrendResponse:
    settings = get_settings(user_id)
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No settings found")
    return get_trend(user_id, settings.goal_weight_kg)
