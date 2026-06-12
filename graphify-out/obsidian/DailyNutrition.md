---
source_file: "api/models/meal.py"
type: "code"
community: "Nutrition Target Checks"
location: "L172"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/Nutrition_Target_Checks
---

# DailyNutrition

## Connections
- [[.test_completes_protein_task_when_target_met()]] - `calls` [EXTRACTED]
- [[.test_does_not_complete_protein_task_when_below_target()]] - `calls` [EXTRACTED]
- [[.test_today_zero_meals_returns_zeros()]] - `calls` [EXTRACTED]
- [[BaseModel]] - `inherits` [EXTRACTED]
- [[Daily nutrition totals with targets, returned by ``GET mealstoday``.      At]] - `rationale_for` [EXTRACTED]
- [[TestAgentAnalyzeMealPhoto]] - `uses` [INFERRED]
- [[TestAgentGetDailyNutrition]] - `uses` [INFERRED]
- [[TestAgentSaveMeal]] - `uses` [INFERRED]
- [[TestAutoCompleteTask]] - `uses` [INFERRED]
- [[TestCheckNutritionTargets]] - `uses` [INFERRED]
- [[TestCompleteTask]] - `uses` [INFERRED]
- [[TestComputeStreak]] - `uses` [INFERRED]
- [[TestGenerateDailyTasksIdempotency]] - `uses` [INFERRED]
- [[TestGetMealsHistory]] - `uses` [INFERRED]
- [[TestGetMealsToday]] - `uses` [INFERRED]
- [[TestGetStatus]] - `uses` [INFERRED]
- [[TestGetTodayTasks]] - `uses` [INFERRED]
- [[TestMealServiceBlankCells]] - `uses` [INFERRED]
- [[TestPostMeals]] - `uses` [INFERRED]
- [[TestPostMealsAnalyze]] - `uses` [INFERRED]
- [[get_meals_today()]] - `calls` [EXTRACTED]
- [[meal.py]] - `contains` [EXTRACTED]
- [[meal_service.py]] - `imports` [EXTRACTED]
- [[meals.py]] - `imports` [EXTRACTED]
- [[test_meal_router.py]] - `imports` [EXTRACTED]
- [[test_missions.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/Nutrition_Target_Checks