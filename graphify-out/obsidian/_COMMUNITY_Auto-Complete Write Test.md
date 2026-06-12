---
type: community
cohesion: 1.00
members: 2
---

# Auto-Complete Write Test

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[.test_completes_task_when_not_yet_done()]] - code - tests/test_missions.py
- [[auto_complete_task writes completed=TRUE when task is pending.]] - rationale - tests/test_missions.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Auto-Complete_Write_Test
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Nutrition Target Checks]]

## Top bridge nodes
- [[.test_completes_task_when_not_yet_done()]] - degree 3, connects to 2 communities