---
type: community
cohesion: 0.12
members: 51
---

# AI Workout Import

**Cohesion:** 0.12 - loosely connected
**Members:** 51 nodes

## Members
- [[3 training + 2 rest days → correct program_days, rest_days, total_exercises.]] - rationale - tests/test_ai_import.py
- [[All 7 days are Rest → program_days=0, total_exercises=0.]] - rationale - tests/test_ai_import.py
- [[Build a list of SimpleNamespace schedule entries from (weekday, day_index) tuple]] - rationale - tests/test_ai_import.py
- [[Critical day_name written to WorkoutSchedules must exactly match the     day_n]] - rationale - tests/test_ai_import.py
- [[Duck-typed stand-in for the locally-defined _ParsedWorkout model.]] - rationale - tests/test_ai_import.py
- [[Every append_row call contains the correct user_id.]] - rationale - tests/test_ai_import.py
- [[Every exercise in a day generates its own append_row to WorkoutPrograms.]] - rationale - tests/test_ai_import.py
- [[ExerciseInfo_2]] - code - tests/test_ai_import.py
- [[If the AI schedules a weekday at a Rest day index, 'Rest' is written correctly.]] - rationale - tests/test_ai_import.py
- [[If the OpenAI call raises, no append_row calls are made.]] - rationale - tests/test_ai_import.py
- [[Indices don't need to match position — index 2 maps to the 3rd day.]] - rationale - tests/test_ai_import.py
- [[One training day + rest → program_days=1.]] - rationale - tests/test_ai_import.py
- [[Plan-based import keeps old plan rows _delete_user_rows is never called.]] - rationale - tests/test_ai_import.py
- [[Regression test for the 'all-Rest schedule' bug.      When parsed.schedule is]] - rationale - tests/test_ai_import.py
- [[Return an ExitStack that wires up all mocks needed by ai_import_workout]] - rationale - tests/test_ai_import.py
- [[Tests for ai_import_workout in apiservicesworkout_service.py.  The Azure Ope]] - rationale - tests/test_ai_import.py
- [[Use AI to parse free-form workout text and import it as a new plan.      Uses]] - rationale - api/services/workout_service.py
- [[When AI returns schedule=None, _auto_schedule cycles days from Monday.]] - rationale - tests/test_ai_import.py
- [[WorkoutDaySummary]] - code - api/models/workout.py
- [[WorkoutDaySummary_4]] - code - tests/test_ai_import.py
- [[WorkoutImportResponse_2]] - code - api/services/workout_service.py
- [[_ai_mocks()]] - code - tests/test_ai_import.py
- [[_ex()]] - code - tests/test_ai_import.py
- [[_parsed()]] - code - tests/test_ai_import.py
- [[_sched()]] - code - tests/test_ai_import.py
- [[ai_import_workout()]] - code - api/services/workout_service.py
- [[day_index in schedule entries is resolved to day_name from the days list.]] - rationale - tests/test_ai_import.py
- [[day_index values outside 0, len(days)) are silently dropped.]] - rationale - tests/test_ai_import.py
- [[parsed=None (model refusedtimed out) raises ValueError before any sheet write.]] - rationale - tests/test_ai_import.py
- [[program_name is written into every WorkoutPrograms row.]] - rationale - tests/test_ai_import.py
- [[schedule= is falsy, so _auto_schedule is used.]] - rationale - tests/test_ai_import.py
- [[sets, rep_min, rep_max, order survive the full pipeline unchanged.]] - rationale - tests/test_ai_import.py
- [[test_ai_import.py]] - code - tests/test_ai_import.py
- [[test_all_out_of_bounds_day_index_falls_back_to_auto_schedule()]] - code - tests/test_ai_import.py
- [[test_auto_schedule_used_when_no_explicit_schedule()]] - code - tests/test_ai_import.py
- [[test_day_index_pointing_to_rest_day_produces_rest_in_schedule()]] - code - tests/test_ai_import.py
- [[test_empty_schedule_list_falls_back_to_auto_schedule()]] - code - tests/test_ai_import.py
- [[test_exercise_fields_reach_response_unchanged()]] - code - tests/test_ai_import.py
- [[test_explicit_schedule_day_index_maps_to_correct_day_name()]] - code - tests/test_ai_import.py
- [[test_explicit_schedule_day_name_matches_program_day_name()]] - code - tests/test_ai_import.py
- [[test_import_is_non_destructive()]] - code - tests/test_ai_import.py
- [[test_multi_exercise_day_all_exercises_written_to_programs()]] - code - tests/test_ai_import.py
- [[test_no_sheet_writes_when_llm_raises()]] - code - tests/test_ai_import.py
- [[test_non_sequential_day_indices_map_correctly()]] - code - tests/test_ai_import.py
- [[test_out_of_bounds_day_index_is_skipped()]] - code - tests/test_ai_import.py
- [[test_parsed_none_raises_value_error_no_sheet_writes()]] - code - tests/test_ai_import.py
- [[test_program_name_propagated_to_workout_programs_rows()]] - code - tests/test_ai_import.py
- [[test_response_counts_ppl_program()]] - code - tests/test_ai_import.py
- [[test_rest_only_program()]] - code - tests/test_ai_import.py
- [[test_single_training_day_program()]] - code - tests/test_ai_import.py
- [[test_user_id_propagated_to_all_append_rows()]] - code - tests/test_ai_import.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/AI_Workout_Import
SORT file.name ASC
```

## Connections to other communities
- 25 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 8 edges to [[_COMMUNITY_Workout Service Queries]]
- 6 edges to [[_COMMUNITY_Workout Text Parser]]
- 3 edges to [[_COMMUNITY_Workout Plan Management]]
- 2 edges to [[_COMMUNITY_Non-Destructive Import Tests]]
- 2 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 1 edge to [[_COMMUNITY_Pydantic AI Agent Core]]
- 1 edge to [[_COMMUNITY_Workout REST Endpoints]]

## Top bridge nodes
- [[WorkoutDaySummary]] - degree 55, connects to 5 communities
- [[ai_import_workout()]] - degree 28, connects to 5 communities
- [[test_ai_import.py]] - degree 26, connects to 1 community
- [[WorkoutDaySummary_4]] - degree 19, connects to 1 community
- [[_ex()]] - degree 18, connects to 1 community