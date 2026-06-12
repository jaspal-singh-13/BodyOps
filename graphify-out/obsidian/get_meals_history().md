---
source_file: "api/services/meal_service.py"
type: "code"
community: "Meal Service Logic"
location: "L204"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Meal_Service_Logic
---

# get_meals_history()

## Connections
- [[MealHistoryDay_2]] - `references` [EXTRACTED]
- [[MealHistoryDay]] - `calls` [EXTRACTED]
- [[Return per-day nutrition summaries for the last ``days`` calendar days.      T]] - `rationale_for` [EXTRACTED]
- [[_fmt_date()]] - `calls` [EXTRACTED]
- [[_weekday_short()]] - `calls` [EXTRACTED]
- [[meal_service.py]] - `contains` [EXTRACTED]
- [[meals.py]] - `imports` [EXTRACTED]
- [[read_rows()]] - `calls` [EXTRACTED]
- [[to_float()]] - `calls` [EXTRACTED]
- [[to_int()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Meal_Service_Logic