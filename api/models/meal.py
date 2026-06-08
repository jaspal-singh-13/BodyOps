"""
Pydantic models for Meal Tracking + AI Vision (Phase 4).

Data flow:
    POST /meals/analyze  → UploadFile (multipart) → AnalyzeMealResponse
    POST /meals          → ConfirmMealRequest      → SavedMealResponse
    GET  /meals/today    →                         → DailyNutrition
    GET  /meals/history  →                         → list[MealHistoryDay]
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


# ---------------------------------------------------------------------------
# Shared / nested
# ---------------------------------------------------------------------------


class MacroTotal(BaseModel):
    """Combined macro totals for a meal or day."""

    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float


class DetectedItem(BaseModel):
    """
    A single food item detected by the vision model.

    Attributes:
        name: Human-readable food name (e.g. "Grilled chicken breast").
        quantity: Amount including unit as a string (e.g. "180 g", "~1 tbsp").
        calories: Estimated kcal for this item.
        protein_g: Estimated protein in grams.
        carbs_g: Estimated carbohydrates in grams.
        fat_g: Estimated fat in grams.
        confidence: AI confidence level — "high", "med", or "low".
    """

    name: str
    quantity: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    confidence: Literal["high", "med", "low"] = "med"


MealType = Literal["Breakfast", "Lunch", "Dinner", "Snack"]


# ---------------------------------------------------------------------------
# Request models
# ---------------------------------------------------------------------------


class ConfirmMealRequest(BaseModel):
    """
    Request body for ``POST /meals`` — save a confirmed meal.

    The ``items`` list is the (possibly user-edited) output from
    ``POST /meals/analyze``. ``drive_url`` is the permanent Drive image URL
    returned by the analyze step; it is passed back so the service layer can
    store it without a second upload.

    Attributes:
        meal_type: Meal slot — Breakfast, Lunch, Dinner, or Snack.
        items: List of food items with macros (editable by the user).
        drive_url: Google Drive public URL for the meal photo. Empty string if
            the meal was entered manually without a photo.
        date: Date of the meal in ``YYYY-MM-DD`` format.
    """

    meal_type: MealType
    items: list[DetectedItem]
    drive_url: str = ""
    date: str  # YYYY-MM-DD


# ---------------------------------------------------------------------------
# Response models
# ---------------------------------------------------------------------------


class AnalyzeMealResponse(BaseModel):
    """
    Response from ``POST /meals/analyze``.

    The analysis result is returned to the client for review — nothing is
    saved to Sheets at this point.  The client sends a ``ConfirmMealRequest``
    to ``POST /meals`` once the user confirms.

    Attributes:
        title: Short human-readable meal label inferred by the model
            (e.g. "Chicken, rice & broccoli").
        confidence: Overall confidence for the whole plate ("high"/"med"/"low").
        detected: Individual food items detected in the image.
        total: Sum of macros across all detected items.
        drive_url: Public Google Drive URL of the uploaded photo.
    """

    title: str
    confidence: Literal["high", "med", "low"]
    detected: list[DetectedItem]
    total: MacroTotal
    drive_url: str


class SavedMealResponse(BaseModel):
    """
    Response from ``POST /meals`` — confirms a meal was saved.

    Attributes:
        meal_id: Unique meal identifier (UUID string).
        meal_type: The meal slot that was saved.
        date: Date the meal was logged.
        total: Total macros for the saved meal.
        daily_nutrition: Updated daily totals after saving this meal.
    """

    meal_id: str
    meal_type: MealType
    date: str
    total: MacroTotal
    daily_nutrition: "DailyNutrition"


class DailyNutrition(BaseModel):
    """
    Daily nutrition totals with targets, returned by ``GET /meals/today``.

    Attributes:
        date: Date in ``YYYY-MM-DD`` format.
        calories: Total kcal consumed today.
        protein_g: Total protein consumed today in grams.
        carbs_g: Total carbs consumed today in grams.
        fat_g: Total fat consumed today in grams.
        target_calories: Daily calorie target from Settings.
        target_protein_g: Daily protein target from Settings.
        target_carbs_g: Daily carb target (calories_remaining / 4 heuristic, or
            set explicitly — stored in Settings).
        target_fat_g: Daily fat target.
        meals_count: Number of distinct meals logged today.
    """

    date: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    target_calories: int
    target_protein_g: float
    target_carbs_g: float
    target_fat_g: float
    meals_count: int


class MealHistoryDay(BaseModel):
    """
    A single day's nutrition summary for the history list.

    Attributes:
        date: Date in ``YYYY-MM-DD`` format.
        display_date: Human-readable label (e.g. "Yesterday · Jun 5").
        meals_count: Number of meals logged that day.
        total_calories: Sum of kcal for all meals.
        total_protein_g: Sum of protein for all meals.
    """

    date: str
    display_date: str
    meals_count: int
    total_calories: int
    total_protein_g: float


class MealRecord(BaseModel):
    """
    A single meal record as returned from the Meals sheet.

    Attributes:
        meal_id: UUID string.
        user_id: Owner's integer user ID.
        date: Date in ``YYYY-MM-DD`` format.
        time: Time in ``HH:MM`` (24-hour) format.
        meal_type: Breakfast / Lunch / Dinner / Snack.
        title: Short label for the meal.
        drive_url: Google Drive photo URL (empty if no photo).
        total: Summed macros for this meal.
        items: Individual food items.
    """

    meal_id: str
    user_id: int
    date: str
    time: str
    meal_type: MealType
    title: str
    drive_url: str
    total: MacroTotal
    items: list[DetectedItem]
