---
source_file: "tests/test_workout_parser.py"
type: "code"
community: "Workout Text Parser"
location: "L1"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Workout_Text_Parser
---

# test_workout_parser.py

## Connections
- [[ExerciseInfo]] - `imports` [EXTRACTED]
- [[Unit tests for apiservicesworkout_parser.py.  All tests call the parser direct]] - `rationale_for` [EXTRACTED]
- [[WorkoutDaySummary]] - `imports` [EXTRACTED]
- [[WorkoutParseError]] - `imports` [EXTRACTED]
- [[_auto_schedule()]] - `imports` [EXTRACTED]
- [[_day()]] - `contains` [EXTRACTED]
- [[parse_workout_import()]] - `imports` [EXTRACTED]
- [[test_auto_schedule_treats_rest_day_as_rest()]] - `contains` [EXTRACTED]
- [[test_auto_schedule_treats_sunday_rest_as_rest()]] - `contains` [EXTRACTED]
- [[test_auto_schedule_treats_verbose_rest_as_rest()]] - `contains` [EXTRACTED]
- [[test_blank_lines_between_blocks_ignored()]] - `contains` [EXTRACTED]
- [[test_empty_schedule_auto_assigns_from_plan()]] - `contains` [EXTRACTED]
- [[test_exercise_before_header_raises()]] - `contains` [EXTRACTED]
- [[test_exercise_order_values()]] - `contains` [EXTRACTED]
- [[test_exercise_with_rep_range()]] - `contains` [EXTRACTED]
- [[test_exercise_without_rep_range()]] - `contains` [EXTRACTED]
- [[test_header_with_slash_parsed()]] - `contains` [EXTRACTED]
- [[test_invalid_exercise_line_raises_with_line_number()]] - `contains` [EXTRACTED]
- [[test_invalid_schedule_line_raises()]] - `contains` [EXTRACTED]
- [[test_rest_day_produces_empty_exercises()]] - `contains` [EXTRACTED]
- [[test_rest_line_case_insensitive()]] - `contains` [EXTRACTED]
- [[test_schedule_case_insensitive()]] - `contains` [EXTRACTED]
- [[test_valid_ppl_plan_exercise_counts()]] - `contains` [EXTRACTED]
- [[test_valid_ppl_plan_parses_day_count()]] - `contains` [EXTRACTED]
- [[test_valid_schedule_text_produces_correct_tuples()]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Workout_Text_Parser