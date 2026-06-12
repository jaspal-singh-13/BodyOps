---
source_file: "api/models/weight.py"
type: "code"
community: "Weight Logging"
location: "L39"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Weight_Logging
---

# WeightEntryCreate

## Connections
- [[._validate_date()_3]] - `method` [EXTRACTED]
- [[._validate_time()_1]] - `method` [EXTRACTED]
- [[._validate_weight()_1]] - `method` [EXTRACTED]
- [[.test_appends_row_when_date_is_new()]] - `calls` [EXTRACTED]
- [[.test_fallback_time_uses_user_timezone()]] - `calls` [EXTRACTED]
- [[.test_invalid_timezone_falls_back_to_utc()]] - `calls` [EXTRACTED]
- [[.test_returns_correct_response_fields()]] - `calls` [EXTRACTED]
- [[.test_updates_row_when_date_already_logged()]] - `calls` [EXTRACTED]
- [[.test_worksheet_not_found_treats_as_empty()]] - `calls` [EXTRACTED]
- [[BaseModel]] - `inherits` [EXTRACTED]
- [[Request body for ``POST weight``.      Attributes         date Date of the]] - `rationale_for` [EXTRACTED]
- [[TestComputeMovingAvg]] - `uses` [INFERRED]
- [[TestGetHistory_1]] - `uses` [INFERRED]
- [[TestLogWeight]] - `uses` [INFERRED]
- [[TestLogWeightTimezoneFallback]] - `uses` [INFERRED]
- [[TestProjectGoalDate]] - `uses` [INFERRED]
- [[_make_weight_logger()]] - `calls` [EXTRACTED]
- [[agent.py_1]] - `imports` [EXTRACTED]
- [[test_weight_service.py]] - `imports` [EXTRACTED]
- [[weight.py]] - `contains` [EXTRACTED]
- [[weight.py_1]] - `imports` [EXTRACTED]
- [[weight_service.py]] - `imports` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Weight_Logging