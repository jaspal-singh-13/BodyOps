import re

from pydantic import BaseModel, field_validator

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


class StepsEntryCreate(BaseModel):
    date: str
    steps: int
    time: str | None = None

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

    @field_validator("steps")
    @classmethod
    def _validate_steps(cls, v: int) -> int:
        if v < 0:
            raise ValueError("steps must be non-negative")
        return v


class StepsEntryResponse(BaseModel):
    user_id: int
    date: str
    time: str
    steps: int
    logged_at: str


class StepsHistoryItem(BaseModel):
    date: str
    time: str
    steps: int
    change_steps: int | None  # None for the oldest entry in the window
