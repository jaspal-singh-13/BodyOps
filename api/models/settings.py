from pydantic import BaseModel


class SettingsCreate(BaseModel):
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
