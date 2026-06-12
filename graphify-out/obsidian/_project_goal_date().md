---
source_file: "api/services/weight_service.py"
type: "code"
community: "Goal Date Projection"
location: "L249"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Goal_Date_Projection
---

# _project_goal_date()

## Connections
- [[.test_correct_projection_simple_linear()]] - `calls` [EXTRACTED]
- [[.test_returns_none_when_too_far_future()]] - `calls` [EXTRACTED]
- [[.test_returns_none_when_trending_up()]] - `calls` [EXTRACTED]
- [[.test_returns_none_with_one_entry()]] - `calls` [EXTRACTED]
- [[.test_uses_last_14_when_more_available()]] - `calls` [EXTRACTED]
- [[Project the date when the user will reach ``goal_weight_kg`` via OLS regression.]] - `rationale_for` [EXTRACTED]
- [[get_trend()]] - `calls` [EXTRACTED]
- [[test_weight_service.py]] - `imports` [EXTRACTED]
- [[weight_service.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Goal_Date_Projection