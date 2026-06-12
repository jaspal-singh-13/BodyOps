---
source_file: "api/services/task_service.py"
type: "code"
community: "Daily Task Service"
location: "L97"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Daily_Task_Service
---

# complete_task()

## Connections
- [[.test_marks_task_completed_and_sets_timestamp()]] - `calls` [EXTRACTED]
- [[.test_no_op_if_already_completed()]] - `calls` [EXTRACTED]
- [[.test_returns_updated_status_response()]] - `calls` [EXTRACTED]
- [[DailyStatusResponse_2]] - `references` [EXTRACTED]
- [[Mark a specific task complete for a given date.      Finds the ``DailyTaskStat]] - `rationale_for` [EXTRACTED]
- [[_build_response()]] - `calls` [EXTRACTED]
- [[_ensure_daily_status()]] - `calls` [EXTRACTED]
- [[_get_task_definitions()]] - `calls` [EXTRACTED]
- [[_make_task_completer()]] - `calls` [EXTRACTED]
- [[_read_daily_status()]] - `calls` [EXTRACTED]
- [[agent.py_1]] - `imports` [EXTRACTED]
- [[read_rows()]] - `calls` [EXTRACTED]
- [[task_service.py]] - `contains` [EXTRACTED]
- [[tasks.py]] - `imports` [EXTRACTED]
- [[test_missions.py]] - `imports` [EXTRACTED]
- [[to_int()]] - `calls` [EXTRACTED]
- [[update_row()]] - `calls` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Daily_Task_Service