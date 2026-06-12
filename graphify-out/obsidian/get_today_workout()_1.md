---
source_file: "api/services/workout_service.py"
type: "code"
community: "Workout Service Queries"
location: "L624"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Workout_Service_Queries
---

# get_today_workout()

## Connections
- [[.test_get_today_workout_all_bad_rows_returns_no_exercises()]] - `calls` [EXTRACTED]
- [[.test_get_today_workout_skips_row_with_empty_exercise_name()]] - `calls` [EXTRACTED]
- [[.test_is_completed_true_when_completed_at_set()]] - `calls` [EXTRACTED]
- [[.test_legacy_fallback_no_plans_rows()]] - `calls` [EXTRACTED]
- [[.test_plan_name_in_response()]] - `calls` [EXTRACTED]
- [[.test_rest_day_returns_no_session_state()]] - `calls` [EXTRACTED]
- [[.test_session_id_is_none_when_no_session_exists()]] - `calls` [EXTRACTED]
- [[.test_session_id_returned_when_session_exists()]] - `calls` [EXTRACTED]
- [[.test_sets_logged_today_counts_only_todays_sets()]] - `calls` [EXTRACTED]
- [[TodayExercise]] - `calls` [EXTRACTED]
- [[TodayWorkoutResponse_2]] - `references` [EXTRACTED]
- [[TodayWorkoutResponse]] - `calls` [EXTRACTED]
- [[_filter_by_plan()]] - `calls` [EXTRACTED]
- [[_get_last_set_from_rows()]] - `calls` [EXTRACTED]
- [[_make_set_logger()]] - `calls` [EXTRACTED]
- [[_make_today_workout_getter()]] - `calls` [EXTRACTED]
- [[_safe_read_rows()]] - `calls` [EXTRACTED]
- [[agent.py_1]] - `imports` [EXTRACTED]
- [[compute_suggestion()]] - `calls` [EXTRACTED]
- [[get_active_plan_id()]] - `calls` [EXTRACTED]
- [[test_workout_service.py]] - `imports` [EXTRACTED]
- [[to_int()]] - `calls` [EXTRACTED]
- [[workout_service.py]] - `contains` [EXTRACTED]
- [[workouts.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Workout_Service_Queries