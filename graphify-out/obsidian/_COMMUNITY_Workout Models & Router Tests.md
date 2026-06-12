---
type: community
cohesion: 0.09
members: 93
---

# Workout Models & Router Tests

**Cohesion:** 0.09 - loosely connected
**Members:** 93 nodes

## Members
- [[.__init__()]] - code - api/services/workout_parser.py
- [[.test_activate_plan_no_auth_returns_401()]] - code - tests/test_workout_router.py
- [[.test_activate_plan_not_found_returns_404()]] - code - tests/test_workout_router.py
- [[.test_activate_plan_success_returns_204()]] - code - tests/test_workout_router.py
- [[.test_ai_import_no_auth_returns_403()]] - code - tests/test_workout_router.py
- [[.test_ai_import_parse_error_returns_422()]] - code - tests/test_workout_router.py
- [[.test_ai_import_success()]] - code - tests/test_workout_router.py
- [[.test_complete_no_auth_returns_403()]] - code - tests/test_workout_router.py
- [[.test_complete_session_returns_204()]] - code - tests/test_workout_router.py
- [[.test_delegates_to_plan_switcher()]] - code - tests/test_workout_router.py
- [[.test_delegates_to_plans_lister()]] - code - tests/test_workout_router.py
- [[.test_delegates_to_progression_getter()]] - code - tests/test_workout_router.py
- [[.test_delegates_to_set_logger_with_correct_args()]] - code - tests/test_workout_router.py
- [[.test_delegates_to_today_workout_getter()]] - code - tests/test_workout_router.py
- [[.test_delegates_to_workout_importer()]] - code - tests/test_workout_router.py
- [[.test_delete_plan_no_auth_returns_401()]] - code - tests/test_workout_router.py
- [[.test_delete_plan_not_found_returns_404()]] - code - tests/test_workout_router.py
- [[.test_delete_plan_success_returns_204()]] - code - tests/test_workout_router.py
- [[.test_emits_tool_call_then_tool_result()_4]] - code - tests/test_workout_router.py
- [[.test_emits_tool_call_then_tool_result()_2]] - code - tests/test_workout_router.py
- [[.test_emits_tool_call_then_tool_result()_5]] - code - tests/test_workout_router.py
- [[.test_emits_tool_call_then_tool_result()_6]] - code - tests/test_workout_router.py
- [[.test_emits_tool_call_then_tool_result()_3]] - code - tests/test_workout_router.py
- [[.test_emits_tool_call_then_tool_result()_7]] - code - tests/test_workout_router.py
- [[.test_get_history_empty_returns_empty_list()_1]] - code - tests/test_workout_router.py
- [[.test_get_history_no_auth_returns_403()]] - code - tests/test_workout_router.py
- [[.test_get_history_returns_sessions()]] - code - tests/test_workout_router.py
- [[.test_get_progression_no_auth_returns_403()]] - code - tests/test_workout_router.py
- [[.test_get_progression_returns_data()]] - code - tests/test_workout_router.py
- [[.test_import_missing_plan_text_returns_422()]] - code - tests/test_workout_router.py
- [[.test_import_no_auth_returns_403()]] - code - tests/test_workout_router.py
- [[.test_import_parse_error_returns_422()]] - code - tests/test_workout_router.py
- [[.test_import_success()]] - code - tests/test_workout_router.py
- [[.test_list_plans_no_auth_returns_401()]] - code - tests/test_workout_router.py
- [[.test_list_plans_returns_plans()]] - code - tests/test_workout_router.py
- [[.test_log_set_invalid_weight_type_returns_422()]] - code - tests/test_workout_router.py
- [[.test_log_set_missing_exercise_name_returns_422()]] - code - tests/test_workout_router.py
- [[.test_log_set_no_auth_returns_403()]] - code - tests/test_workout_router.py
- [[.test_log_set_success()]] - code - tests/test_workout_router.py
- [[.test_schedule_day_structure()]] - code - tests/test_workout_router.py
- [[.test_schedule_empty_program_returns_all_rest()]] - code - tests/test_workout_router.py
- [[.test_schedule_no_auth_returns_401()]] - code - tests/test_workout_router.py
- [[.test_schedule_rest_day_has_no_exercises()]] - code - tests/test_workout_router.py
- [[.test_schedule_returns_7_days()]] - code - tests/test_workout_router.py
- [[.test_today_no_auth_returns_403()]] - code - tests/test_workout_router.py
- [[.test_today_returns_rest_day()]] - code - tests/test_workout_router.py
- [[.test_today_returns_workout()]] - code - tests/test_workout_router.py
- [[AgentDeps_1]] - code - api/agent/deps.py
- [[AiWorkoutImportRequest]] - code - api/models/workout.py
- [[BaseModel]] - code
- [[CompleteSessionRequest]] - code - api/models/workout.py
- [[Dependency container passed to every Pydantic AI tool via ``RunContext.deps``.]] - rationale - api/agent/deps.py
- [[ExerciseInfo]] - code - api/models/workout.py
- [[ExerciseProgressionResponse]] - code - api/models/workout.py
- [[LogSetResponse]] - code - api/models/workout.py
- [[ProgressionSuggestion]] - code - api/models/workout.py
- [[Pydantic models for the Workout System (Phase 3).  Request models  WorkoutImp]] - rationale - api/models/workout.py
- [[Queue_1]] - code - tests/test_workout_router.py
- [[RenamePlanRequest]] - code - api/models/workout.py
- [[ScheduleDay]] - code - api/models/workout.py
- [[TestDeletePlanEndpoint]] - code - tests/test_workout_router.py
- [[TestGetProgressionTargetTool]] - code - tests/test_workout_router.py
- [[TestGetTodayWorkoutTool]] - code - tests/test_workout_router.py
- [[TestGetWorkoutsHistory]] - code - tests/test_workout_router.py
- [[TestGetWorkoutsPlans]] - code - tests/test_workout_router.py
- [[TestGetWorkoutsProgression]] - code - tests/test_workout_router.py
- [[TestGetWorkoutsSchedule]] - code - tests/test_workout_router.py
- [[TestGetWorkoutsToday]] - code - tests/test_workout_router.py
- [[TestImportWorkoutFromTextTool]] - code - tests/test_workout_router.py
- [[TestListWorkoutPlansTool]] - code - tests/test_workout_router.py
- [[TestLogWorkoutSetTool]] - code - tests/test_workout_router.py
- [[TestPostActivatePlan]] - code - tests/test_workout_router.py
- [[TestPostWorkoutsAiImport]] - code - tests/test_workout_router.py
- [[TestPostWorkoutsComplete]] - code - tests/test_workout_router.py
- [[TestPostWorkoutsImport]] - code - tests/test_workout_router.py
- [[TestPostWorkoutsLog]] - code - tests/test_workout_router.py
- [[TestSwitchWorkoutPlanTool]] - code - tests/test_workout_router.py
- [[Tests for the workout system API routes and agent tools.  Router tests POST]] - rationale - tests/test_workout_router.py
- [[TodayExercise]] - code - api/models/workout.py
- [[TodayWorkoutResponse]] - code - api/models/workout.py
- [[UpdateDayRequest]] - code - api/models/workout.py
- [[UpdateScheduleWeekdayRequest]] - code - api/models/workout.py
- [[WorkoutHistoryResponse]] - code - api/models/workout.py
- [[WorkoutImportRequest]] - code - api/models/workout.py
- [[WorkoutImportResponse]] - code - api/models/workout.py
- [[WorkoutParseError]] - code - api/services/workout_parser.py
- [[WorkoutPlanSummary]] - code - api/models/workout.py
- [[WorkoutPlansResponse]] - code - api/models/workout.py
- [[WorkoutScheduleResponse]] - code - api/models/workout.py
- [[_make_ctx()_1]] - code - tests/test_workout_router.py
- [[_make_workout_deps()]] - code - tests/test_workout_router.py
- [[test_workout_router.py]] - code - tests/test_workout_router.py
- [[workout.py]] - code - api/models/workout.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workout_Models__Router_Tests
SORT file.name ASC
```

## Connections to other communities
- 25 edges to [[_COMMUNITY_AI Workout Import]]
- 15 edges to [[_COMMUNITY_Workout REST Endpoints]]
- 15 edges to [[_COMMUNITY_Workout Plan Management]]
- 15 edges to [[_COMMUNITY_Workout Service Queries]]
- 10 edges to [[_COMMUNITY_Pydantic AI Agent Core]]
- 9 edges to [[_COMMUNITY_Workout Text Parser]]
- 6 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 6 edges to [[_COMMUNITY_Agent Tools Tests]]
- 5 edges to [[_COMMUNITY_Meal Models & Router Tests]]
- 3 edges to [[_COMMUNITY_Meal Macro Schemas]]
- 3 edges to [[_COMMUNITY_Task Models & Router Tests]]
- 3 edges to [[_COMMUNITY_Weight Models & Router Tests]]
- 2 edges to [[_COMMUNITY_App Entry & Login]]
- 2 edges to [[_COMMUNITY_Nutrition Target Checks]]
- 2 edges to [[_COMMUNITY_Non-Destructive Import Tests]]
- 2 edges to [[_COMMUNITY_Set Logging & Progression]]
- 1 edge to [[_COMMUNITY_Meal Service Logic]]
- 1 edge to [[_COMMUNITY_Settings Validation Models]]
- 1 edge to [[_COMMUNITY_Weight Logging]]
- 1 edge to [[_COMMUNITY_Progression Suggestion Tests]]
- 1 edge to [[_COMMUNITY_Auth & JWT Tests]]

## Top bridge nodes
- [[BaseModel]] - degree 42, connects to 11 communities
- [[ExerciseInfo]] - degree 41, connects to 5 communities
- [[workout.py]] - degree 25, connects to 5 communities
- [[AgentDeps_1]] - degree 39, connects to 3 communities
- [[WorkoutParseError]] - degree 28, connects to 3 communities