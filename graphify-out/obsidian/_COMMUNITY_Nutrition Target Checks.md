---
type: community
cohesion: 0.14
members: 24
---

# Nutrition Target Checks

**Cohesion:** 0.14 - loosely connected
**Members:** 24 nodes

## Members
- [[.test_appends_rows_when_none_exist()]] - code - tests/test_missions.py
- [[.test_completes_protein_task_when_target_met()]] - code - tests/test_missions.py
- [[.test_does_not_complete_protein_task_when_below_target()]] - code - tests/test_missions.py
- [[.test_does_not_duplicate_rows_when_called_twice()]] - code - tests/test_missions.py
- [[.test_no_op_if_no_task_definition()]] - code - tests/test_missions.py
- [[.test_today_zero_meals_returns_zeros()]] - code - tests/test_meal_router.py
- [[Check if protein and calorie targets have been met; auto-complete those tasks.]] - rationale - api/services/task_service.py
- [[Daily nutrition totals with targets, returned by ``GET mealstoday``.      At]] - rationale - api/models/meal.py
- [[DailyNutrition]] - code - api/models/meal.py
- [[DailyTaskStatus rows are created when the date has no entries.]] - rationale - tests/test_missions.py
- [[DailyTaskStatus rows are not appended a second time if they already exist.]] - rationale - tests/test_missions.py
- [[Response shape for ``GET settings`` and ``POST settings``.      Identical to]] - rationale - api/models/settings.py
- [[SettingsResponse]] - code - api/models/settings.py
- [[TestAutoCompleteTask]] - code - tests/test_missions.py
- [[TestCheckNutritionTargets]] - code - tests/test_missions.py
- [[TestGenerateDailyTasksIdempotency]] - code - tests/test_missions.py
- [[TestGetStatus]] - code - tests/test_missions.py
- [[TestGetTodayTasks]] - code - tests/test_missions.py
- [[Unit tests for apiservicestask_service.py.]] - rationale - tests/test_missions.py
- [[auto_complete_task silently does nothing when task_type has no definition.]] - rationale - tests/test_missions.py
- [[check_nutrition_targets completes hit_protein when consumed = target.]] - rationale - tests/test_missions.py
- [[check_nutrition_targets does not complete hit_protein when under target.]] - rationale - tests/test_missions.py
- [[check_nutrition_targets()]] - code - api/services/task_service.py
- [[test_missions.py]] - code - tests/test_missions.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Nutrition_Target_Checks
SORT file.name ASC
```

## Connections to other communities
- 12 edges to [[_COMMUNITY_Daily Task Service]]
- 9 edges to [[_COMMUNITY_Meal Models & Router Tests]]
- 6 edges to [[_COMMUNITY_Settings Service & Router]]
- 4 edges to [[_COMMUNITY_Streak Computation Tests]]
- 4 edges to [[_COMMUNITY_Weight Models & Router Tests]]
- 3 edges to [[_COMMUNITY_Meal Service Logic]]
- 3 edges to [[_COMMUNITY_Complete Task Tests]]
- 2 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 2 edges to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 1 edge to [[_COMMUNITY_Meal Analyzer Factory Tests]]
- 1 edge to [[_COMMUNITY_Meal Analyze Endpoint Tests]]
- 1 edge to [[_COMMUNITY_Rest Day Tasks Test]]
- 1 edge to [[_COMMUNITY_Completion Percentage Test]]
- 1 edge to [[_COMMUNITY_Workout Day Tasks Test]]
- 1 edge to [[_COMMUNITY_Auto-Complete Write Test]]
- 1 edge to [[_COMMUNITY_Auto-Complete No-Op Test]]
- 1 edge to [[_COMMUNITY_Status Totals Test]]

## Top bridge nodes
- [[DailyNutrition]] - degree 26, connects to 8 communities
- [[SettingsResponse]] - degree 21, connects to 5 communities
- [[check_nutrition_targets()]] - degree 10, connects to 4 communities
- [[test_missions.py]] - degree 18, connects to 3 communities
- [[TestGetTodayTasks]] - degree 6, connects to 3 communities