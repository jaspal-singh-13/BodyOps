---
type: community
cohesion: 0.38
members: 10
---

# Non-Destructive Import Tests

**Cohesion:** 0.38 - loosely connected
**Members:** 10 nodes

## Members
- [[._run_import()]] - code - tests/test_workout_service.py
- [[.test_all_7_weekdays_written_when_schedule_is_complete()]] - code - tests/test_workout_service.py
- [[.test_creates_new_plan_row()]] - code - tests/test_workout_service.py
- [[.test_empty_schedule_fills_all_7_as_rest()]] - code - tests/test_workout_service.py
- [[.test_missing_weekdays_filled_with_rest()]] - code - tests/test_workout_service.py
- [[.test_no_duplicate_weekdays()]] - code - tests/test_workout_service.py
- [[.test_plan_row_contains_plan_id()]] - code - tests/test_workout_service.py
- [[.test_program_rows_stamped_with_plan_id()]] - code - tests/test_workout_service.py
- [[.test_schedule_rows_stamped_with_plan_id()]] - code - tests/test_workout_service.py
- [[TestImportWorkoutNonDestructive]] - code - tests/test_workout_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Non-Destructive_Import_Tests
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 2 edges to [[_COMMUNITY_AI Workout Import]]
- 1 edge to [[_COMMUNITY_Workout Plan Management]]
- 1 edge to [[_COMMUNITY_Workout Service Queries]]

## Top bridge nodes
- [[TestImportWorkoutNonDestructive]] - degree 12, connects to 3 communities
- [[._run_import()]] - degree 12, connects to 3 communities