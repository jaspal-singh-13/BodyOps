"""
Pydantic models for user settings.

Settings are scoped to a single user (``user_id``) and stored in the
``Settings`` tab of the Main Data Sheet — one row per user.

``SettingsCreate`` is used for both initial onboarding (POST) and
subsequent updates. ``SettingsResponse`` is the read shape returned
by GET; it adds ``updated_at`` which the service layer writes on save.
"""

import re
from typing import Literal

from pydantic import BaseModel, field_validator

_DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


class SettingsCreate(BaseModel):
    """
    Request body for ``POST /settings`` (onboarding + updates).

    Attributes:
        name: Display name.
        current_weight_kg: Starting body weight in kilograms (must be positive).
        height_cm: Height in centimetres (must be positive).
        age: Age in years (must be positive).
        goal_weight_kg: Target body weight in kilograms (must be positive).
        start_date: Tracking start date in ``YYYY-MM-DD`` format.
        calorie_target: Daily calorie intake target (kcal, must be positive).
        protein_target_g: Daily protein intake target (grams, must be positive).
        wake_up_time: Preferred wake-up time in ``HH:MM`` (24-hour) format,
            used to schedule daily mission generation.
        unit_preference: ``"metric"`` (kg/cm) or ``"imperial"`` (lbs/in).
            Defaults to ``"metric"``.
        reminders_json: JSON-encoded reminder configuration stored as a
            string in the sheet. Defaults to ``"{}"``.
    """

    name: str
    current_weight_kg: float
    height_cm: float
    age: int
    goal_weight_kg: float
    start_date: str
    calorie_target: int
    protein_target_g: int
    wake_up_time: str
    unit_preference: Literal["metric", "imperial"] = "metric"
    reminders_json: str = "{}"

    @field_validator("start_date")
    @classmethod
    def _validate_start_date(cls, v: str) -> str:
        if not _DATE_RE.match(v):
            raise ValueError("start_date must be in YYYY-MM-DD format")
        return v

    @field_validator("wake_up_time")
    @classmethod
    def _validate_wake_up_time(cls, v: str) -> str:
        if not _TIME_RE.match(v):
            raise ValueError("wake_up_time must be in HH:MM (24-hour) format")
        return v

    @field_validator("current_weight_kg", "goal_weight_kg")
    @classmethod
    def _validate_weight(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("weight values must be positive")
        return v

    @field_validator("height_cm")
    @classmethod
    def _validate_height(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("height_cm must be positive")
        return v

    @field_validator("age")
    @classmethod
    def _validate_age(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("age must be positive")
        return v

    @field_validator("calorie_target", "protein_target_g")
    @classmethod
    def _validate_targets(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("calorie and protein targets must be positive")
        return v


class SettingsResponse(BaseModel):
    """
    Response shape for ``GET /settings`` and ``POST /settings``.

    Identical to ``SettingsCreate`` plus ``updated_at`` which records the
    ISO 8601 UTC timestamp of the last save.

    Attributes:
        updated_at: ISO 8601 UTC timestamp of the last update, or ``""``
            if not yet written (e.g. freshly created row without a flush).
    """

    user_id: int
    name: str
    current_weight_kg: float
    height_cm: float
    age: int
    goal_weight_kg: float
    start_date: str
    calorie_target: int
    protein_target_g: int
    wake_up_time: str
    unit_preference: str = "metric"
    reminders_json: str = "{}"
    updated_at: str = ""
