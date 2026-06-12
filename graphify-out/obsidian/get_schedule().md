---
source_file: "api/services/workout_service.py"
type: "code"
community: "Workout Service Queries"
location: "L938"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Workout_Service_Queries
---

# get_schedule()

## Connections
- [[.test_always_returns_7_days()]] - `calls` [EXTRACTED]
- [[.test_exercises_mapped_to_correct_day()]] - `calls` [EXTRACTED]
- [[.test_get_schedule_skips_row_with_empty_exercise_name()]] - `calls` [EXTRACTED]
- [[.test_get_schedule_skips_row_with_missing_exercise_name_key()]] - `calls` [EXTRACTED]
- [[.test_ignores_rows_from_other_plans()]] - `calls` [EXTRACTED]
- [[.test_legacy_fallback_no_plans_tab()]] - `calls` [EXTRACTED]
- [[.test_missing_weekdays_default_to_rest()]] - `calls` [EXTRACTED]
- [[.test_no_schedule_no_program_returns_all_rest_and_no_program_name()]] - `calls` [EXTRACTED]
- [[.test_program_name_from_plans_tab()]] - `calls` [EXTRACTED]
- [[.test_rest_day_has_empty_exercises()]] - `calls` [EXTRACTED]
- [[.test_weekdays_are_in_order_mon_to_sun()]] - `calls` [EXTRACTED]
- [[ExerciseInfo_1]] - `calls` [EXTRACTED]
- [[ExerciseInfo]] - `calls` [EXTRACTED]
- [[ScheduleDay]] - `calls` [EXTRACTED]
- [[WorkoutScheduleResponse_2]] - `references` [EXTRACTED]
- [[WorkoutScheduleResponse]] - `calls` [EXTRACTED]
- [[_filter_by_plan()]] - `calls` [EXTRACTED]
- [[_safe_read_rows()]] - `calls` [EXTRACTED]
- [[get_active_plan_id()]] - `calls` [EXTRACTED]
- [[test_workout_service.py]] - `imports` [EXTRACTED]
- [[to_int()]] - `calls` [EXTRACTED]
- [[workout_service.py]] - `contains` [EXTRACTED]
- [[workouts.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Workout_Service_Queries