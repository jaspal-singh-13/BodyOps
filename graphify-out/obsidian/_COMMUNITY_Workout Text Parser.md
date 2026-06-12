---
type: community
cohesion: 0.09
members: 38
---

# Workout Text Parser

**Cohesion:** 0.09 - loosely connected
**Members:** 38 nodes

## Members
- [[AiWorkoutImportRequest_1]] - code - api/routers/workouts.py
- [[Cycle non-rest days over Mon–Sun; remaining slots get 'Rest'.]] - rationale - api/services/workout_parser.py
- [[Parse workout plan text and optional schedule text.      Returns         (days,]] - rationale - api/services/workout_parser.py
- [[Rest Day' (with suffix) must also be treated as rest.]] - rationale - tests/test_workout_parser.py
- [[Sunday — Rest' produced by AI should be treated as rest.]] - rationale - tests/test_workout_parser.py
- [[Thursday — Rest' must not occupy a weekday slot.]] - rationale - tests/test_workout_parser.py
- [[Unit tests for apiservicesworkout_parser.py.  All tests call the parser direct]] - rationale - tests/test_workout_parser.py
- [[Workout plan text parser.  Public API ---------- parse_workout_import(plan_text,]] - rationale - api/services/workout_parser.py
- [[WorkoutDaySummary_1]] - code - api/services/workout_parser.py
- [[WorkoutImportRequest_1]] - code - api/routers/workouts.py
- [[WorkoutImportResponse_1]] - code - api/routers/workouts.py
- [[_auto_schedule()]] - code - api/services/workout_parser.py
- [[_day()]] - code - tests/test_workout_parser.py
- [[_parse_plan()]] - code - api/services/workout_parser.py
- [[_parse_schedule()]] - code - api/services/workout_parser.py
- [[ai_import_workout_endpoint()]] - code - api/routers/workouts.py
- [[import_workout_endpoint()]] - code - api/routers/workouts.py
- [[parse_workout_import()]] - code - api/services/workout_parser.py
- [[test_auto_schedule_treats_rest_day_as_rest()]] - code - tests/test_workout_parser.py
- [[test_auto_schedule_treats_sunday_rest_as_rest()]] - code - tests/test_workout_parser.py
- [[test_auto_schedule_treats_verbose_rest_as_rest()]] - code - tests/test_workout_parser.py
- [[test_blank_lines_between_blocks_ignored()]] - code - tests/test_workout_parser.py
- [[test_empty_schedule_auto_assigns_from_plan()]] - code - tests/test_workout_parser.py
- [[test_exercise_before_header_raises()]] - code - tests/test_workout_parser.py
- [[test_exercise_order_values()]] - code - tests/test_workout_parser.py
- [[test_exercise_with_rep_range()]] - code - tests/test_workout_parser.py
- [[test_exercise_without_rep_range()]] - code - tests/test_workout_parser.py
- [[test_header_with_slash_parsed()]] - code - tests/test_workout_parser.py
- [[test_invalid_exercise_line_raises_with_line_number()]] - code - tests/test_workout_parser.py
- [[test_invalid_schedule_line_raises()]] - code - tests/test_workout_parser.py
- [[test_rest_day_produces_empty_exercises()]] - code - tests/test_workout_parser.py
- [[test_rest_line_case_insensitive()]] - code - tests/test_workout_parser.py
- [[test_schedule_case_insensitive()]] - code - tests/test_workout_parser.py
- [[test_valid_ppl_plan_exercise_counts()]] - code - tests/test_workout_parser.py
- [[test_valid_ppl_plan_parses_day_count()]] - code - tests/test_workout_parser.py
- [[test_valid_schedule_text_produces_correct_tuples()]] - code - tests/test_workout_parser.py
- [[test_workout_parser.py]] - code - tests/test_workout_parser.py
- [[workout_parser.py]] - code - api/services/workout_parser.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workout_Text_Parser
SORT file.name ASC
```

## Connections to other communities
- 9 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 6 edges to [[_COMMUNITY_AI Workout Import]]
- 4 edges to [[_COMMUNITY_Workout REST Endpoints]]
- 1 edge to [[_COMMUNITY_Workout Plan Management]]

## Top bridge nodes
- [[workout_parser.py]] - degree 10, connects to 3 communities
- [[test_workout_parser.py]] - degree 25, connects to 2 communities
- [[_auto_schedule()]] - degree 10, connects to 2 communities
- [[_parse_plan()]] - degree 6, connects to 2 communities
- [[_day()]] - degree 6, connects to 2 communities