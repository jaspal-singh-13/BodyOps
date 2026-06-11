"""
Pydantic models for daily missions / tasks.

Tasks are stored in two sheet tabs:
  - ``Tasks``           — task definitions (one row per task type per user)
  - ``DailyTaskStatus`` — one row per task per day, tracks completion

``TaskResponse``         — a single task with its daily completion state.
``DailyStatusResponse``  — the full daily mission list with aggregated counts.
``CompleteTaskRequest``  — body for ``POST /tasks/complete``.
"""

import re

from pydantic import BaseModel, field_validator

_DATE_RE = re.compile(r"^\d{4}-(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])$")


class TaskResponse(BaseModel):
    """
    A single task with its completion state for a specific day.

    Attributes:
        id: UUID string from the ``Tasks`` sheet row.
        name: Human-readable task name (e.g. "Log your weight").
        description: Short description shown in the UI.
        task_type: Machine-readable type key used for auto-completion hooks.
        completed: Whether the task has been marked complete for the day.
        completed_at: ISO 8601 UTC timestamp of completion, or ``None``.
    """

    id: str
    name: str
    description: str
    task_type: str
    completed: bool
    completed_at: str | None = None


class DailyStatusResponse(BaseModel):
    """
    The full daily mission list for a user on a given date.

    Attributes:
        date: The date these missions apply to (``YYYY-MM-DD``).
        tasks: Ordered list of tasks with completion state.
        total: Total number of tasks for the day.
        completed: Number of completed tasks.
        percentage: Completion percentage (0–100, rounded to 1 decimal).
    """

    date: str
    tasks: list[TaskResponse]
    total: int
    completed: int
    percentage: float


class CompleteTaskRequest(BaseModel):
    """
    Request body for ``POST /tasks/complete``.

    Attributes:
        task_id: The ``id`` from the ``Tasks`` sheet row to mark complete.
        date: The date the task should be marked complete for (``YYYY-MM-DD``).
    """

    task_id: str
    date: str

    @field_validator("date")
    @classmethod
    def _validate_date(cls, v: str) -> str:
        if not _DATE_RE.match(v):
            raise ValueError("date must be in YYYY-MM-DD format")
        return v
