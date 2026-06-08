"""
Meals router — meal photo analysis, confirmation, and history.

Endpoints:
    POST /meals/analyze  — upload a meal photo, run AI vision, return analysis.
    POST /meals          — save a confirmed meal to the Sheets.
    GET  /meals/today    — return today's meals and daily nutrition totals.
    GET  /meals/history  — return per-day summaries for the last 30 days.

All endpoints require a valid JWT.  The analyze endpoint is intentionally
kept separate from the save endpoint so the user can review and edit the
AI-detected items before committing them to the database.
"""

from __future__ import annotations

import asyncio

from fastapi import APIRouter, Depends, Header, HTTPException, UploadFile, status

from ..auth import get_current_user
from ..models.meal import (
    AnalyzeMealResponse,
    ConfirmMealRequest,
    DailyNutrition,
    MealHistoryDay,
    SavedMealResponse,
)
from ..services.drive_service import upload_meal_image
from ..services.meal_service import (
    get_meal_records_today,
    get_meals_history,
    get_meals_today,
    save_meal,
)
from ..services.meal_vision import analyze_meal

router = APIRouter(prefix="/meals", tags=["meals"])

_ALLOWED_MIME = {"image/jpeg", "image/png", "image/webp", "image/heic", "image/heif"}


@router.post("/analyze", response_model=AnalyzeMealResponse)
async def analyze_meal_endpoint(
    file: UploadFile,
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> AnalyzeMealResponse:
    """
    Upload a meal photo, store it in Google Drive, and run AI vision analysis.

    The analysis result is returned for the user to review and edit — nothing
    is written to the Meals or MealItems sheets at this point.  Call
    ``POST /meals`` with the confirmed payload to persist the meal.

    Args:
        file: Multipart image file (JPEG, PNG, WebP, HEIC).

    Returns:
        ``AnalyzeMealResponse`` with detected food items, macro estimates,
        totals, and the Drive URL of the uploaded photo.

    Raises:
        400: If the uploaded file is not a recognised image type.
        422: If the AI returns an unparseable response.
        500: On Drive upload or OpenAI API failure.
    """
    mime = file.content_type or "image/jpeg"
    if mime not in _ALLOWED_MIME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported image type '{mime}'. Allowed: jpeg, png, webp.",
        )

    data = await file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Uploaded file is empty."
        )

    try:
        drive_url = await upload_meal_image(data, mime)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Drive upload failed: {exc}",
        ) from exc

    try:
        result = await analyze_meal(drive_url, drive_url)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Vision analysis failed: {exc}",
        ) from exc

    return result


@router.post("", response_model=SavedMealResponse, status_code=status.HTTP_201_CREATED)
async def save_meal_endpoint(
    body: ConfirmMealRequest,
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> SavedMealResponse:
    """
    Save a confirmed meal (and its items) to the Sheets.

    The ``items`` list should be the (possibly user-edited) list from the
    analysis step.  The ``drive_url`` from the analysis response must be passed
    back here so it can be stored with the meal record.

    Returns:
        ``SavedMealResponse`` with the new meal ID and updated daily totals.
    """
    return await asyncio.to_thread(save_meal, user_id, body, x_timezone)


@router.get("/today", response_model=DailyNutrition)
async def get_today_endpoint(
    user_id: int = Depends(get_current_user),
    x_timezone: str = Header(default="UTC", alias="X-Timezone"),
) -> DailyNutrition:
    """
    Return today's nutrition totals and targets for the authenticated user.

    Resolves "today" using the ``X-Timezone`` header so that the correct
    calendar date is used regardless of the user's location.

    Returns:
        ``DailyNutrition`` with consumed macros, targets, and meal count.
    """
    return await asyncio.to_thread(get_meals_today, user_id, x_timezone)


@router.get("/history", response_model=list[MealHistoryDay])
async def get_history_endpoint(
    user_id: int = Depends(get_current_user),
) -> list[MealHistoryDay]:
    """
    Return per-day nutrition summaries for the last 30 days.

    Days with no meals are omitted.  The list is sorted newest first.

    Returns:
        List of ``MealHistoryDay`` objects.
    """
    return await asyncio.to_thread(get_meals_history, user_id)
