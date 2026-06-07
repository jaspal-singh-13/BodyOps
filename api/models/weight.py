from pydantic import BaseModel


class WeightEntryCreate(BaseModel):
    date: str        # YYYY-MM-DD
    weight_kg: float


class WeightEntryResponse(BaseModel):
    user_id: int
    date: str
    weight_kg: float
    logged_at: str


class WeightHistoryItem(BaseModel):
    date: str
    weight_kg: float
    change_kg: float | None  # diff from previous entry; None for oldest entry


class WeightTrendResponse(BaseModel):
    moving_avg: list[dict]           # [{date, weight_kg, ma_7: float|None}]
    total_loss_kg: float | None      # None if fewer than 2 entries
    projected_goal_date: str | None  # YYYY-MM-DD or None
