---
type: community
cohesion: 1.00
members: 2
---

# Auto-Complete No-Op Test

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[.test_no_op_if_task_already_completed()]] - code - tests/test_missions.py
- [[auto_complete_task does not write if the task is already marked done.]] - rationale - tests/test_missions.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Auto-Complete_No-Op_Test
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Nutrition Target Checks]]

## Top bridge nodes
- [[.test_no_op_if_task_already_completed()]] - degree 3, connects to 2 communities