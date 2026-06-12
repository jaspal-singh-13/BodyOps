---
type: community
cohesion: 1.00
members: 2
---

# Completion Percentage Test

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[.test_percentage_reflects_completed_tasks()]] - code - tests/test_missions.py
- [[percentage is computed correctly when some tasks are done.]] - rationale - tests/test_missions.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Completion_Percentage_Test
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Nutrition Target Checks]]

## Top bridge nodes
- [[.test_percentage_reflects_completed_tasks()]] - degree 3, connects to 2 communities