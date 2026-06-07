"""
Pydantic models for user settings.

Settings are scoped to a single user (``user_id``) and stored in the
``Settings`` tab of the Main Data Sheet — one row per user.

``SettingsCreate`` is used for both initial onboarding (POST) and
subsequent updates. ``SettingsResponse`` is the read shape returned
by GET; it adds ``updated_at`` which the service layer writes on save.
"""

from pydantic import BaseModel


class SettingsCreate(BaseModel):
    """
    Request body for ``POST /settings`` (onboarding + updates).

    Attributes:
        user_id: Integer user ID — must match the authenticated user.
        name: Display name.
        current_weight_kg: Starting body weight in kilograms.
        height_cm: Height in centimetres (used for BMR calculation).
        age: Age in years (used for BMR calculation).
        goal_weight_kg: Target body weight in kilograms.
        start_date: Tracking start date in ``YYYY-MM-DD`` format.
        calorie_target: Daily calorie intake target (kcal).
        protein_target_g: Daily protein intake target (grams).
        wake_up_time: Preferred wake-up time in ``HH:MM`` (24-hour) format,
            used to schedule daily mission generation.
        unit_preference: ``"metric"`` (kg/cm) or ``"imperial"`` (lbs/in).
            Defaults to ``"metric"``.
        reminders_json: JSON-encoded reminder configuration stored as a
            string in the sheet. Defaults to ``"{}"``.
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
