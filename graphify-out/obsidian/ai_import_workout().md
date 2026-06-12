---
source_file: "api/services/workout_service.py"
type: "code"
community: "AI Workout Import"
location: "L864"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/AI_Workout_Import
---

# ai_import_workout()

## Connections
- [[Use AI to parse free-form workout text and import it as a new plan.      Uses]] - `rationale_for` [EXTRACTED]
- [[WorkoutImportResponse_2]] - `references` [EXTRACTED]
- [[_auto_schedule()]] - `calls` [EXTRACTED]
- [[_make_workout_importer()]] - `calls` [EXTRACTED]
- [[agent.py_1]] - `imports` [EXTRACTED]
- [[ai_import_workout_endpoint()]] - `calls` [EXTRACTED]
- [[get_async_client()]] - `calls` [EXTRACTED]
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
- [[test_no_sheet_writes_when_llm_raises()]] - `calls` [EXTRACTED]
- [[test_non_sequential_day_indices_map_correctly()]] - `calls` [EXTRACTED]
- [[test_out_of_bounds_day_index_is_skipped()]] - `calls` [EXTRACTED]
- [[test_parsed_none_raises_value_error_no_sheet_writes()]] - `calls` [EXTRACTED]
- [[test_program_name_propagated_to_workout_programs_rows()]] - `calls` [EXTRACTED]
- [[test_response_counts_ppl_program()]] - `calls` [EXTRACTED]
- [[test_rest_only_program()]] - `calls` [EXTRACTED]
- [[test_single_training_day_program()]] - `calls` [EXTRACTED]
- [[test_user_id_propagated_to_all_append_rows()]] - `calls` [EXTRACTED]
- [[workout_service.py]] - `contains` [EXTRACTED]
- [[workouts.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/AI_Workout_Import