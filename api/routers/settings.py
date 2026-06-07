from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import get_current_user
from ..models.settings import SettingsCreate, SettingsResponse
from ..services.settings_service import get_settings, save_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings_endpoint(
    _email: str = Depends(get_current_user),
) -> SettingsResponse:
    settings = get_settings()
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No settings found")
    return settings


@router.post("", response_model=SettingsResponse)
async def save_settings_endpoint(
    body: SettingsCreate,
    _email: str = Depends(get_current_user),
) -> SettingsResponse:
    return save_settings(body)
