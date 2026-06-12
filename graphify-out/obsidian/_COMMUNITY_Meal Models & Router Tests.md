---
type: community
cohesion: 0.09
members: 41
---

# Meal Models & Router Tests

**Cohesion:** 0.09 - loosely connected
**Members:** 41 nodes

## Members
- [[._calories_non_negative()_1]] - code - api/models/meal.py
- [[._macros_non_negative()_1]] - code - api/models/meal.py
- [[._validate_date()]] - code - api/models/meal.py
- [[.test_fmt_date_is_platform_independent()]] - code - tests/test_meal_router.py
- [[.test_get_daily_nutrition_delegates()]] - code - tests/test_meal_router.py
- [[.test_get_meals_today_skips_blank_numeric_cells()]] - code - tests/test_meal_router.py
- [[.test_history_empty_returns_empty_list()]] - code - tests/test_meal_router.py
- [[.test_history_no_auth_returns_401()]] - code - tests/test_meal_router.py
- [[.test_history_returns_list()]] - code - tests/test_meal_router.py
- [[.test_save_meal_agent_tool_callable()]] - code - tests/test_meal_router.py
- [[.test_save_meal_invalid_meal_type_returns_422()]] - code - tests/test_meal_router.py
- [[.test_save_meal_no_auth_returns_401()]] - code - tests/test_meal_router.py
- [[.test_save_meal_success()]] - code - tests/test_meal_router.py
- [[.test_today_no_auth_returns_401()]] - code - tests/test_meal_router.py
- [[.test_today_returns_daily_nutrition()]] - code - tests/test_meal_router.py
- [[A meal row with blank totals (gspread returns ) must not 500 the endpoint.]] - rationale - tests/test_meal_router.py
- [[A single day's nutrition summary for the history list.      Attributes]] - rationale - api/models/meal.py
- [[A single food item detected by the vision model.      Attributes         nam]] - rationale - api/models/meal.py
- [[AnalyzeMealResponse]] - code - api/models/meal.py
- [[ConfirmMealRequest]] - code - api/models/meal.py
- [[DetectedItem]] - code - api/models/meal.py
- [[MealHistoryDay]] - code - api/models/meal.py
- [[Pydantic models for Meal Tracking + AI Vision (Phase 4).  Data flow     POST]] - rationale - api/models/meal.py
- [[Request body for ``POST meals`` — save a confirmed meal.      The ``items`` l]] - rationale - api/models/meal.py
- [[Response from ``POST mealsanalyze``.      The analysis result is returned to]] - rationale - api/models/meal.py
- [[Response from ``POST meals`` — confirms a meal was saved.      Attributes]] - rationale - api/models/meal.py
- [[Return an async callable that saves a meal from free-form item dicts.]] - rationale - api/routers/agent.py
- [[SavedMealResponse]] - code - api/models/meal.py
- [[TestAgentGetDailyNutrition]] - code - tests/test_meal_router.py
- [[TestAgentSaveMeal]] - code - tests/test_meal_router.py
- [[TestGetMealsHistory]] - code - tests/test_meal_router.py
- [[TestGetMealsToday]] - code - tests/test_meal_router.py
- [[TestMealServiceBlankCells]] - code - tests/test_meal_router.py
- [[TestPostMeals]] - code - tests/test_meal_router.py
- [[Tests for the meals API routes and Phase 4 agent tools.  Router tests POST m]] - rationale - tests/test_meal_router.py
- [[The meal_saver factory produces a callable that saves a meal.]] - rationale - tests/test_meal_router.py
- [[_fmt_date renders Jun 5 without the Unix-only %-d flag.]] - rationale - tests/test_meal_router.py
- [[_make_meal_saver()]] - code - api/routers/agent.py
- [[get_daily_nutrition tool calls the injected nutrition_getter callable.]] - rationale - tests/test_meal_router.py
- [[meal.py]] - code - api/models/meal.py
- [[test_meal_router.py]] - code - tests/test_meal_router.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Meal_Models__Router_Tests
SORT file.name ASC
```

## Connections to other communities
- 13 edges to [[_COMMUNITY_Meal Macro Schemas]]
- 13 edges to [[_COMMUNITY_Meal Service Logic]]
- 9 edges to [[_COMMUNITY_Nutrition Target Checks]]
- 8 edges to [[_COMMUNITY_Meal Analyzer Factory Tests]]
- 6 edges to [[_COMMUNITY_Meal Vision Service]]
- 6 edges to [[_COMMUNITY_Meal Analyze Endpoint Tests]]
- 5 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 5 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 5 edges to [[_COMMUNITY_Meals Router & Auth Dependency]]

## Top bridge nodes
- [[DetectedItem]] - degree 22, connects to 7 communities
- [[AnalyzeMealResponse]] - degree 17, connects to 6 communities
- [[ConfirmMealRequest]] - degree 17, connects to 6 communities
- [[SavedMealResponse]] - degree 16, connects to 6 communities
- [[test_meal_router.py]] - degree 21, connects to 5 communities