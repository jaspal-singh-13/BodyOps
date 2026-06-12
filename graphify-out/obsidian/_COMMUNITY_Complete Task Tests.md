---
type: community
cohesion: 0.29
members: 7
---

# Complete Task Tests

**Cohesion:** 0.29 - loosely connected
**Members:** 7 nodes

## Members
- [[.test_marks_task_completed_and_sets_timestamp()]] - code - tests/test_missions.py
- [[.test_no_op_if_already_completed()]] - code - tests/test_missions.py
- [[.test_returns_updated_status_response()]] - code - tests/test_missions.py
- [[TestCompleteTask]] - code - tests/test_missions.py
- [[complete_task does not write if task is already done.]] - rationale - tests/test_missions.py
- [[complete_task returns DailyStatusResponse with updated counts.]] - rationale - tests/test_missions.py
- [[complete_task updates the correct row with completed=TRUE.]] - rationale - tests/test_missions.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Complete_Task_Tests
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Nutrition Target Checks]]
- 3 edges to [[_COMMUNITY_Daily Task Service]]

## Top bridge nodes
- [[TestCompleteTask]] - degree 6, connects to 1 community
- [[.test_marks_task_completed_and_sets_timestamp()]] - degree 3, connects to 1 community
- [[.test_no_op_if_already_completed()]] - degree 3, connects to 1 community
- [[.test_returns_updated_status_response()]] - degree 3, connects to 1 community