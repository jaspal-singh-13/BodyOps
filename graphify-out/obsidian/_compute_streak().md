---
source_file: "api/services/task_service.py"
type: "code"
community: "Daily Task Service"
location: "L357"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Daily_Task_Service
---

# _compute_streak()

## Connections
- [[.test_complete_today_extends_streak()]] - `calls` [EXTRACTED]
- [[.test_gap_breaks_streak()]] - `calls` [EXTRACTED]
- [[.test_incomplete_today_does_not_break_existing_streak()]] - `calls` [EXTRACTED]
- [[.test_no_rows_returns_zero()]] - `calls` [EXTRACTED]
- [[Count consecutive fully-complete days ending on or before ``today``.      Scan]] - `rationale_for` [EXTRACTED]
- [[_build_response()]] - `calls` [EXTRACTED]
- [[read_rows()]] - `calls` [EXTRACTED]
- [[task_service.py]] - `contains` [EXTRACTED]
- [[test_missions.py]] - `imports` [EXTRACTED]
- [[to_int()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Daily_Task_Service