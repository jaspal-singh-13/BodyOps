---
type: community
cohesion: 0.09
members: 64
---

# Workout Service Queries

**Cohesion:** 0.09 - loosely connected
**Members:** 64 nodes

## Members
- [[._make_patch()]] - code - tests/test_workout_service.py
- [[._make_patch()_1]] - code - tests/test_workout_service.py
- [[._make_schedule_patch()]] - code - tests/test_workout_service.py
- [[._make_today_patch()]] - code - tests/test_workout_service.py
- [[.test_activates_target_plan()]] - code - tests/test_workout_service.py
- [[.test_active_flag_correct()]] - code - tests/test_workout_service.py
- [[.test_always_returns_7_days()]] - code - tests/test_workout_service.py
- [[.test_deactivates_active_plan_before_deleting()]] - code - tests/test_workout_service.py
- [[.test_deletes_plan_rows_and_plan_entry()]] - code - tests/test_workout_service.py
- [[.test_empty_returns_empty_list()]] - code - tests/test_workout_service.py
- [[.test_exercise_count_per_plan()]] - code - tests/test_workout_service.py
- [[.test_exercises_mapped_to_correct_day()]] - code - tests/test_workout_service.py
- [[.test_get_schedule_skips_row_with_empty_exercise_name()]] - code - tests/test_workout_service.py
- [[.test_get_schedule_skips_row_with_missing_exercise_name_key()]] - code - tests/test_workout_service.py
- [[.test_get_today_workout_all_bad_rows_returns_no_exercises()]] - code - tests/test_workout_service.py
- [[.test_get_today_workout_skips_row_with_empty_exercise_name()]] - code - tests/test_workout_service.py
- [[.test_ignores_other_users_plans()]] - code - tests/test_workout_service.py
- [[.test_ignores_rows_from_other_plans()]] - code - tests/test_workout_service.py
- [[.test_is_completed_true_when_completed_at_set()]] - code - tests/test_workout_service.py
- [[.test_legacy_fallback_no_plans_rows()]] - code - tests/test_workout_service.py
- [[.test_legacy_fallback_no_plans_tab()]] - code - tests/test_workout_service.py
- [[.test_missing_weekdays_default_to_rest()]] - code - tests/test_workout_service.py
- [[.test_no_schedule_no_program_returns_all_rest_and_no_program_name()]] - code - tests/test_workout_service.py
- [[.test_plan_name_in_response()]] - code - tests/test_workout_service.py
- [[.test_program_name_from_plans_tab()]] - code - tests/test_workout_service.py
- [[.test_raises_when_plan_not_found()]] - code - tests/test_workout_service.py
- [[.test_raises_when_plan_not_found()_1]] - code - tests/test_workout_service.py
- [[.test_rest_day_has_empty_exercises()]] - code - tests/test_workout_service.py
- [[.test_rest_day_returns_no_session_state()]] - code - tests/test_workout_service.py
- [[.test_returns_active_plan_id()]] - code - tests/test_workout_service.py
- [[.test_returns_all_user_plans()]] - code - tests/test_workout_service.py
- [[.test_returns_none_when_no_active_row_for_user()]] - code - tests/test_workout_service.py
- [[.test_returns_none_when_no_plans_tab()]] - code - tests/test_workout_service.py
- [[.test_session_id_is_none_when_no_session_exists()]] - code - tests/test_workout_service.py
- [[.test_session_id_returned_when_session_exists()]] - code - tests/test_workout_service.py
- [[.test_sets_logged_today_counts_only_todays_sets()]] - code - tests/test_workout_service.py
- [[.test_weekdays_are_in_order_mon_to_sun()]] - code - tests/test_workout_service.py
- [[Deleting the active plan deactivates it first instead of raising.]] - rationale - tests/test_workout_service.py
- [[ExerciseInfo_1]] - code - api/services/workout_service.py
- [[Exercises from a different plan_id must not bleed into the active plan's schedul]] - rationale - tests/test_workout_service.py
- [[Legacy mode no PLANS_TAB rows → filters by user_id only.]] - rationale - tests/test_workout_service.py
- [[Return all saved plans for the user with name, active flag, and dayexercise cou]] - rationale - api/services/workout_service.py
- [[TestActivatePlan]] - code - tests/test_workout_service.py
- [[TestDeletePlan]] - code - tests/test_workout_service.py
- [[TestGetActivePlanId]] - code - tests/test_workout_service.py
- [[TestGetSchedule]] - code - tests/test_workout_service.py
- [[TestGetTodayWorkoutSessionState]] - code - tests/test_workout_service.py
- [[TestListPlans]] - code - tests/test_workout_service.py
- [[TestMissingExerciseNameRows]] - code - tests/test_workout_service.py
- [[TodayWorkoutResponse_2]] - code - api/services/workout_service.py
- [[Unit tests for workout_service functions.  Covers   - get_schedule 7-day st]] - rationale - tests/test_workout_service.py
- [[With no WorkoutPlans rows (legacy), all user rows are returned.]] - rationale - tests/test_workout_service.py
- [[WorkoutPlansResponse_2]] - code - api/services/workout_service.py
- [[WorkoutScheduleResponse_2]] - code - api/services/workout_service.py
- [[_plan_row()]] - code - tests/test_workout_service.py
- [[_program_row()]] - code - tests/test_workout_service.py
- [[_schedule_row()]] - code - tests/test_workout_service.py
- [[_session_row()]] - code - tests/test_workout_service.py
- [[_set_row()]] - code - tests/test_workout_service.py
- [[get_schedule and get_today_workout must never crash on rows that have     exerc]] - rationale - tests/test_workout_service.py
- [[get_schedule()]] - code - api/services/workout_service.py
- [[get_today_workout()_1]] - code - api/services/workout_service.py
- [[list_plans()]] - code - api/services/workout_service.py
- [[test_workout_service.py]] - code - tests/test_workout_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workout_Service_Queries
SORT file.name ASC
```

## Connections to other communities
- 18 edges to [[_COMMUNITY_Workout Plan Management]]
- 15 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 9 edges to [[_COMMUNITY_Set Logging & Progression]]
- 8 edges to [[_COMMUNITY_AI Workout Import]]
- 5 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 3 edges to [[_COMMUNITY_Workout REST Endpoints]]
- 1 edge to [[_COMMUNITY_Progression Suggestion Tests]]
- 1 edge to [[_COMMUNITY_Non-Destructive Import Tests]]

## Top bridge nodes
- [[get_today_workout()_1]] - degree 24, connects to 6 communities
- [[test_workout_service.py]] - degree 23, connects to 5 communities
- [[get_schedule()]] - degree 23, connects to 4 communities
- [[list_plans()]] - degree 16, connects to 4 communities
- [[TestGetSchedule]] - degree 13, connects to 2 communities