---
source_file: "api/services/weight_service.py"
type: "code"
community: "Weight Logging"
location: "L43"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Weight_Logging
---

# log_weight()

## Connections
- [[.test_appends_row_when_date_is_new()]] - `calls` [EXTRACTED]
- [[.test_fallback_time_uses_user_timezone()]] - `calls` [EXTRACTED]
- [[.test_invalid_timezone_falls_back_to_utc()]] - `calls` [EXTRACTED]
- [[.test_returns_correct_response_fields()]] - `calls` [EXTRACTED]
- [[.test_updates_row_when_date_already_logged()]] - `calls` [EXTRACTED]
- [[.test_worksheet_not_found_treats_as_empty()]] - `calls` [EXTRACTED]
- [[Upsert a weight entry append if the date+time is new, update if it exists.]] - `rationale_for` [EXTRACTED]
- [[WeightEntryCreate_2]] - `references` [EXTRACTED]
- [[WeightEntryResponse_2]] - `references` [EXTRACTED]
- [[WeightEntryResponse]] - `calls` [EXTRACTED]
- [[_make_weight_logger()]] - `calls` [EXTRACTED]
- [[agent.py_1]] - `imports` [EXTRACTED]
- [[append_row()]] - `calls` [EXTRACTED]
- [[read_rows()]] - `calls` [EXTRACTED]
- [[test_weight_service.py]] - `imports` [EXTRACTED]
- [[to_int()]] - `calls` [EXTRACTED]
- [[update_row()]] - `calls` [EXTRACTED]
- [[weight.py_1]] - `imports` [EXTRACTED]
- [[weight_service.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Weight_Logging