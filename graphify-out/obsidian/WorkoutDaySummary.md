---
source_file: "api/models/workout.py"
type: "code"
community: "AI Workout Import"
location: "L34"
tags:
  - graphify/code
  - graphify/INFERRED
  - community/AI_Workout_Import
---

# WorkoutDaySummary

## Connections
- [[._run_import()]] - `calls` [EXTRACTED]
- [[BaseModel]] - `inherits` [EXTRACTED]
- [[ExerciseInfo_2]] - `uses` [INFERRED]
- [[Queue_1]] - `uses` [INFERRED]
- [[TestActivatePlan]] - `uses` [INFERRED]
- [[TestDeletePlan]] - `uses` [INFERRED]
- [[TestDeletePlanEndpoint]] - `uses` [INFERRED]
- [[TestGetActivePlanId]] - `uses` [INFERRED]
- [[TestGetProgressionTargetTool]] - `uses` [INFERRED]
- [[TestGetSchedule]] - `uses` [INFERRED]
- [[TestGetTodayWorkoutSessionState]] - `uses` [INFERRED]
- [[TestGetTodayWorkoutTool]] - `uses` [INFERRED]
- [[TestGetWorkoutsHistory]] - `uses` [INFERRED]
- [[TestGetWorkoutsPlans]] - `uses` [INFERRED]
- [[TestGetWorkoutsProgression]] - `uses` [INFERRED]
- [[TestGetWorkoutsSchedule]] - `uses` [INFERRED]
- [[TestGetWorkoutsToday]] - `uses` [INFERRED]
- [[TestImportWorkoutFromTextTool]] - `uses` [INFERRED]
- [[TestImportWorkoutNonDestructive]] - `uses` [INFERRED]
- [[TestListPlans]] - `uses` [INFERRED]
- [[TestListWorkoutPlansTool]] - `uses` [INFERRED]
- [[TestLogWorkoutSetTool]] - `uses` [INFERRED]
- [[TestMissingExerciseNameRows]] - `uses` [INFERRED]
- [[TestPostActivatePlan]] - `uses` [INFERRED]
- [[TestPostWorkoutsAiImport]] - `uses` [INFERRED]
- [[TestPostWorkoutsComplete]] - `uses` [INFERRED]
- [[TestPostWorkoutsImport]] - `uses` [INFERRED]
- [[TestPostWorkoutsLog]] - `uses` [INFERRED]
- [[TestSwitchWorkoutPlanTool]] - `uses` [INFERRED]
- [[WorkoutDaySummary_4]] - `uses` [INFERRED]
- [[_day()]] - `calls` [EXTRACTED]
- [[_parse_plan()]] - `calls` [EXTRACTED]
- [[test_ai_import.py]] - `imports` [EXTRACTED]
- [[test_all_out_of_bounds_day_index_falls_back_to_auto_schedule()]] - `calls` [EXTRACTED]
- [[test_auto_schedule_used_when_no_explicit_schedule()]] - `calls` [EXTRACTED]
- [[test_day_index_pointing_to_rest_day_produces_rest_in_schedule()]] - `calls` [EXTRACTED]
- [[test_empty_schedule_list_falls_back_to_auto_schedule()]] - `calls` [EXTRACTED]
- [[test_exercise_fields_reach_response_unchanged()]] - `calls` [EXTRACTED]
- [[test_explicit_schedule_day_index_maps_to_correct_day_name()]] - `calls` [EXTRACTED]
- [[test_explicit_schedule_day_name_matches_program_day_name()]] - `calls` [EXTRACTED]
- [[test_import_is_non_destructive()]] - `calls` [EXTRACTED]
- [[test_multi_exercise_day_all_exercises_written_to_programs()]] - `calls` [EXTRACTED]
- [[test_non_sequential_day_indices_map_correctly()]] - `calls` [EXTRACTED]
- [[test_out_of_bounds_day_index_is_skipped()]] - `calls` [EXTRACTED]
- [[test_program_name_propagated_to_workout_programs_rows()]] - `calls` [EXTRACTED]
- [[test_response_counts_ppl_program()]] - `calls` [EXTRACTED]
- [[test_rest_only_program()]] - `calls` [EXTRACTED]
- [[test_single_training_day_program()]] - `calls` [EXTRACTED]
- [[test_user_id_propagated_to_all_append_rows()]] - `calls` [EXTRACTED]
- [[test_workout_parser.py]] - `imports` [EXTRACTED]
- [[test_workout_router.py]] - `imports` [EXTRACTED]
- [[test_workout_service.py]] - `imports` [EXTRACTED]
- [[workout.py]] - `contains` [EXTRACTED]
- [[workout_parser.py]] - `imports` [EXTRACTED]
- [[workout_service.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/INFERRED #community/AI_Workout_Import