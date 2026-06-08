"""
Pydantic models for weight tracking.

Data flow:
    POST /weight  → WeightEntryCreate  → WeightEntryResponse
    GET  /history → list[WeightHistoryItem]
    GET  /trend   → WeightTrendResponse
"""

import re

from pydantic import BaseModel, field_validator

# ---------------------------------------------------------------------------
# Shared regex patterns
# ---------------------------------------------------------------------------

_DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")
_TIME_RE = re.compile(r"^([01]\d|2[0-3]):[0-5]\d$")


def _check_date(v: str) -> str:
    if not _DATE_RE.match(v):
        raise ValueError("date must be in YYYY-MM-DD format")
    return v


def _check_time(v: str) -> str:
    if not _TIME_RE.match(v):
        raise ValueError("time must be in HH:MM (24-hour) format")
    return v


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class WeightEntryCreate(BaseModel):
    """
    Request body for ``POST /weight``.

    Attributes:
        date: Date of the weigh-in in ``YYYY-MM-DD`` format.
        weight_kg: Body weight in kilograms (must be positive).
        time: Time of the weigh-in in ``HH:MM`` (24-hour) format. Defaults to
            the current local time when omitted, allowing multiple entries per day.
    """

    date: str        # YYYY-MM-DD
    weight_kg: float
    time: str | None = None  # HH:MM — defaults to current time in service layer

    @field_validator("date")
    @classmethod
    def _validate_date(cls, v: str) -> str:
        return _check_date(v)

    @field_validator("time")
    @classmethod
    def _validate_time(cls, v: str | None) -> str | None:
        if v is not None:
            return _check_time(v)
        return v

    @field_validator("weight_kg")
    @classmethod
    def _validate_weight(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("weight_kg must be a positive number")
        return v


class WeightEntryResponse(BaseModel):
    """
    Response returned after a successful weight log (POST /weight).

    Attributes:
        user_id: Authenticated user's integer ID.
        date: Date of the weigh-in in ``YYYY-MM-DD`` format.
        time: Time of the weigh-in in ``HH:MM`` format.
        weight_kg: Logged body weight in kilograms.
        logged_at: ISO 8601 UTC timestamp when the entry was written.
    """

    user_id: int
    date: str
    time: str
    weight_kg: float
    logged_at: str


class WeightHistoryItem(BaseModel):
    """
    A single entry in the weight history list (GET /weight/history).

    Attributes:
        date: Date in ``YYYY-MM-DD`` format.
        time: Time of the weigh-in in ``HH:MM`` format.
        weight_kg: Body weight in kilograms.
        change_kg: Difference from the previous chronological entry (positive
            means gained, negative means lost). ``None`` for the oldest entry
            in the returned window (no prior entry to diff against).
    """

    date: str
    time: str
    weight_kg: float
    change_kg: float | None  # None for the oldest entry in the window


class WeightTrendResponse(BaseModel):
    """
    Trend analytics returned by GET /weight/trend.

    Attributes:
        moving_avg: Chronological list of ``{date, weight_kg, ma_7}`` dicts.
            ``ma_7`` is the 7-day moving average (``None`` for the first 6 entries
            where fewer than 7 data points exist).
        total_loss_kg: Total weight lost since the first logged entry
            (first − last, so positive = loss). ``None`` if fewer than 2 entries.
        projected_goal_date: ISO ``YYYY-MM-DD`` date when the user is projected
            to reach ``goal_weight_kg`` based on linear regression over the last
            14 weigh-ins. ``None`` if the trend is flat/rising or the projection
            is more than 5 years away.
    """

    moving_avg: list[dict]           # [{date, weight_kg, ma_7: float|None}]
    total_loss_kg: float | None      # None if fewer than 2 entries
    projected_goal_date: str | None  # YYYY-MM-DD or None
