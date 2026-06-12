---
source_file: "api/services/task_service.py"
type: "code"
community: "Nutrition Target Checks"
location: "L199"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Nutrition_Target_Checks
---

# check_nutrition_targets()

## Connections
- [[.test_completes_protein_task_when_target_met()]] - `calls` [EXTRACTED]
- [[.test_does_not_complete_protein_task_when_below_target()]] - `calls` [EXTRACTED]
- [[Check if protein and calorie targets have been met; auto-complete those tasks.]] - `rationale_for` [EXTRACTED]
- [[_resolve_today()]] - `calls` [EXTRACTED]
- [[auto_complete_task()]] - `calls` [EXTRACTED]
- [[get_meals_today()]] - `calls` [EXTRACTED]
- [[get_settings()]] - `calls` [EXTRACTED]
- [[meals.py]] - `imports` [EXTRACTED]
- [[task_service.py]] - `contains` [EXTRACTED]
- [[test_missions.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Nutrition_Target_Checks