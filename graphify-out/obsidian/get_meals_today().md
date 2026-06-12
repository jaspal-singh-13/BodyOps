---
source_file: "api/services/meal_service.py"
type: "code"
community: "Meal Service Logic"
location: "L146"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Meal_Service_Logic
---

# get_meals_today()

## Connections
- [[.test_get_meals_today_skips_blank_numeric_cells()]] - `calls` [EXTRACTED]
- [[DailyNutrition_2]] - `references` [EXTRACTED]
- [[DailyNutrition]] - `calls` [EXTRACTED]
- [[Return today's meals summed into a ``DailyNutrition`` object.      Resolves t]] - `rationale_for` [EXTRACTED]
- [[_get_targets()]] - `calls` [EXTRACTED]
- [[_make_nutrition_getter()]] - `calls` [EXTRACTED]
- [[agent.py_1]] - `imports` [EXTRACTED]
- [[check_nutrition_targets()]] - `calls` [EXTRACTED]
- [[meal_service.py]] - `contains` [EXTRACTED]
- [[meals.py]] - `imports` [EXTRACTED]
- [[read_rows()]] - `calls` [EXTRACTED]
- [[save_meal()_1]] - `calls` [EXTRACTED]
- [[task_service.py]] - `imports` [EXTRACTED]
- [[test_meal_router.py]] - `imports` [EXTRACTED]
- [[to_float()]] - `calls` [EXTRACTED]
- [[to_int()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Meal_Service_Logic