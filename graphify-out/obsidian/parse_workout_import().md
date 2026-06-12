---
source_file: "api/services/workout_parser.py"
type: "code"
community: "Workout Text Parser"
location: "L140"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Workout_Text_Parser
---

# parse_workout_import()

## Connections
- [[Parse workout plan text and optional schedule text.      Returns         (days,]] - `rationale_for` [EXTRACTED]
- [[WorkoutDaySummary_1]] - `references` [EXTRACTED]
- [[_auto_schedule()]] - `calls` [EXTRACTED]
- [[_parse_plan()]] - `calls` [EXTRACTED]
- [[_parse_schedule()]] - `calls` [EXTRACTED]
- [[import_workout_endpoint()]] - `calls` [EXTRACTED]
- [[test_blank_lines_between_blocks_ignored()]] - `calls` [EXTRACTED]
- [[test_empty_schedule_auto_assigns_from_plan()]] - `calls` [EXTRACTED]
- [[test_exercise_before_header_raises()]] - `calls` [EXTRACTED]
- [[test_exercise_order_values()]] - `calls` [EXTRACTED]
- [[test_exercise_with_rep_range()]] - `calls` [EXTRACTED]
- [[test_exercise_without_rep_range()]] - `calls` [EXTRACTED]
- [[test_header_with_slash_parsed()]] - `calls` [EXTRACTED]
- [[test_invalid_exercise_line_raises_with_line_number()]] - `calls` [EXTRACTED]
- [[test_invalid_schedule_line_raises()]] - `calls` [EXTRACTED]
- [[test_rest_day_produces_empty_exercises()]] - `calls` [EXTRACTED]
- [[test_rest_line_case_insensitive()]] - `calls` [EXTRACTED]
- [[test_schedule_case_insensitive()]] - `calls` [EXTRACTED]
- [[test_valid_ppl_plan_exercise_counts()]] - `calls` [EXTRACTED]
- [[test_valid_ppl_plan_parses_day_count()]] - `calls` [EXTRACTED]
- [[test_valid_schedule_text_produces_correct_tuples()]] - `calls` [EXTRACTED]
- [[test_workout_parser.py]] - `imports` [EXTRACTED]
- [[workout_parser.py]] - `contains` [EXTRACTED]
- [[workouts.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Workout_Text_Parser