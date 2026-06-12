---
source_file: "api/services/workout_parser.py"
type: "code"
community: "Workout Text Parser"
location: "L121"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Workout_Text_Parser
---

# _auto_schedule()

## Connections
- [[Cycle non-rest days over Mon–Sun; remaining slots get 'Rest'.]] - `rationale_for` [EXTRACTED]
- [[WorkoutDaySummary_1]] - `references` [EXTRACTED]
- [[ai_import_workout()]] - `calls` [EXTRACTED]
- [[parse_workout_import()]] - `calls` [EXTRACTED]
- [[test_auto_schedule_treats_rest_day_as_rest()]] - `calls` [EXTRACTED]
- [[test_auto_schedule_treats_sunday_rest_as_rest()]] - `calls` [EXTRACTED]
- [[test_auto_schedule_treats_verbose_rest_as_rest()]] - `calls` [EXTRACTED]
- [[test_workout_parser.py]] - `imports` [EXTRACTED]
- [[workout_parser.py]] - `contains` [EXTRACTED]
- [[workout_service.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Workout_Text_Parser