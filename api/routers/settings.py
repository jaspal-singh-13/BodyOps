"""
Settings router — user profile and onboarding data.

Endpoints:
    GET  /settings  — load the authenticated user's current settings row.
    POST /settings  — create or update the settings row (upsert by user_id).

Both endpoints require a valid JWT. The service layer scopes all reads/writes
to the authenticated ``user_id``, so one user can never read another's settings.
"""

import asyncio

from fastapi import APIRouter, Depends, HTTPException, status

from ..auth import get_current_user
from ..models.settings import SettingsCreate, SettingsResponse
from ..services.settings_service import get_reminders, get_settings, save_reminders, save_settings

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=SettingsResponse)
async def get_settings_endpoint(
    user_id: int = Depends(get_current_user),
) -> SettingsResponse:
    """
    Return the authenticated user's settings row.

    Used by the frontend on every page load to check if onboarding is complete.
    A 404 response means no settings row exists yet — the client should redirect
    to ``/onboarding``.

    Returns:
        ``SettingsResponse`` with all profile and target fields.

    Raises:
        HTTPException(404): If no settings row exists for this user.
    """
    settings = await asyncio.to_thread(get_settings, user_id)
    if settings is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No settings found")
    return settings


@router.post("", response_model=SettingsResponse)
async def save_settings_endpoint(
    body: SettingsCreate,
    user_id: int = Depends(get_current_user),
) -> SettingsResponse:
    """
    Create or update the authenticated user's settings row (upsert).

    The service layer checks whether a row already exists for this ``user_id``:
    if so it updates in place; otherwise it appends a new row. The ``user_id``
    from the JWT takes precedence over any ``user_id`` in the request body.

    Args:
        body: Full settings payload including all profile and target fields.

    Returns:
        ``SettingsResponse`` reflecting the saved state, including ``updated_at``.
    """
    return await asyncio.to_thread(save_settings, user_id, body)


@router.get("/reminders", response_model=dict)
async def get_reminders_endpoint(
    user_id: int = Depends(get_current_user),
) -> dict:
    """
    Return the authenticated user's reminder configuration.

    Returns:
        Dict parsed from the ``reminders_json`` Settings field, or ``{}``
        if no reminders have been configured yet.
    """
    return await asyncio.to_thread(get_reminders, user_id)


@router.post("/reminders", response_model=dict)
async def save_reminders_endpoint(
    body: dict,
    user_id: int = Depends(get_current_user),
) -> dict:
    """
    Save the authenticated user's reminder configuration.

    The entire reminders dict is replaced on each call. Stored as JSON
    in the ``reminders_json`` field of the Settings row.

    Args:
        body: Reminder config dict, e.g.
            ``{"weigh_in": {"enabled": true, "time": "07:00"}}``.

    Returns:
        The saved reminders dict.

    Raises:
        HTTPException(404): If no settings row exists (onboarding not complete).
    """
    try:
        return await asyncio.to_thread(save_reminders, user_id, body)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
