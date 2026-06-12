---
source_file: "tests/test_workout_service.py"
type: "code"
community: "Workout Service Queries"
location: "L612"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Workout_Service_Queries
---

# TestMissingExerciseNameRows

## Connections
- [[._make_schedule_patch()]] - `method` [EXTRACTED]
- [[._make_today_patch()]] - `method` [EXTRACTED]
- [[.test_get_schedule_skips_row_with_empty_exercise_name()]] - `method` [EXTRACTED]
- [[.test_get_schedule_skips_row_with_missing_exercise_name_key()]] - `method` [EXTRACTED]
- [[.test_get_today_workout_all_bad_rows_returns_no_exercises()]] - `method` [EXTRACTED]
- [[.test_get_today_workout_skips_row_with_empty_exercise_name()]] - `method` [EXTRACTED]
- [[ExerciseInfo]] - `uses` [INFERRED]
- [[WorkoutDaySummary]] - `uses` [INFERRED]
- [[get_schedule and get_today_workout must never crash on rows that have     exerc]] - `rationale_for` [EXTRACTED]
- [[test_workout_service.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Workout_Service_Queries