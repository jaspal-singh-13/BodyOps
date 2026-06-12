---
type: community
cohesion: 0.09
members: 31
---

# Meal Service Logic

**Cohesion:** 0.09 - loosely connected
**Members:** 31 nodes

## Members
- [[._validate_date()_1]] - code - api/models/meal.py
- [[._validate_time()]] - code - api/models/meal.py
- [[A single meal record as returned from the Meals sheet.      Attributes]] - rationale - api/models/meal.py
- [[Any_2]] - code - api/sheets/sheets_repo.py
- [[Build a short title from the first 1–3 item names.]] - rationale - api/services/meal_service.py
- [[Business logic for meal tracking.  Reads from and writes to the ``Meals`` and]] - rationale - api/services/meal_service.py
- [[ConfirmMealRequest_2]] - code - api/services/meal_service.py
- [[DailyNutrition_2]] - code - api/services/meal_service.py
- [[DetectedItem_1]] - code - api/services/meal_service.py
- [[Format YYYY-MM-DD as 'Jun 5'.]] - rationale - api/services/meal_service.py
- [[MealHistoryDay_2]] - code - api/services/meal_service.py
- [[MealRecord_1]] - code - api/services/meal_service.py
- [[MealRecord]] - code - api/models/meal.py
- [[Persist a confirmed meal and its items to the Sheets.      Appends one row to]] - rationale - api/services/meal_service.py
- [[Return (calorie_target, protein_g, carbs_g, fat_g) from Settings.]] - rationale - api/services/meal_service.py
- [[Return 3-letter weekday name e.g. 'Mon'.]] - rationale - api/services/meal_service.py
- [[Return ``value`` as float, or ``default`` if it cannot be converted.]] - rationale - api/sheets/sheets_repo.py
- [[Return full meal records for today including items.      Args         user_i]] - rationale - api/services/meal_service.py
- [[Return per-day nutrition summaries for the last ``days`` calendar days.      T]] - rationale - api/services/meal_service.py
- [[Return today's meals summed into a ``DailyNutrition`` object.      Resolves t]] - rationale - api/services/meal_service.py
- [[SavedMealResponse_2]] - code - api/services/meal_service.py
- [[_fmt_date()]] - code - api/services/meal_service.py
- [[_get_targets()]] - code - api/services/meal_service.py
- [[_make_title()]] - code - api/services/meal_service.py
- [[_weekday_short()]] - code - api/services/meal_service.py
- [[get_meal_records_today()]] - code - api/services/meal_service.py
- [[get_meals_history()]] - code - api/services/meal_service.py
- [[get_meals_today()]] - code - api/services/meal_service.py
- [[meal_service.py]] - code - api/services/meal_service.py
- [[save_meal()_1]] - code - api/services/meal_service.py
- [[to_float()]] - code - api/sheets/sheets_repo.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Meal_Service_Logic
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_Meal Models & Router Tests]]
- 8 edges to [[_COMMUNITY_Sheets Repo Helpers]]
- 7 edges to [[_COMMUNITY_Workout Plan Management]]
- 6 edges to [[_COMMUNITY_Settings Service & Router]]
- 6 edges to [[_COMMUNITY_Daily Task Service]]
- 5 edges to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 4 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 3 edges to [[_COMMUNITY_Meal Macro Schemas]]
- 3 edges to [[_COMMUNITY_Nutrition Target Checks]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 1 edge to [[_COMMUNITY_Workout Models & Router Tests]]
- 1 edge to [[_COMMUNITY_Set Logging & Progression]]

## Top bridge nodes
- [[meal_service.py]] - degree 29, connects to 10 communities
- [[get_meals_today()]] - degree 16, connects to 6 communities
- [[save_meal()_1]] - degree 12, connects to 5 communities
- [[get_meal_records_today()]] - degree 11, connects to 5 communities
- [[to_float()]] - degree 11, connects to 4 communities