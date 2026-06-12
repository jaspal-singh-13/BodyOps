---
type: community
cohesion: 1.00
members: 2
---

# Rest Day Tasks Test

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[.test_omits_workout_task_on_rest_day()]] - code - tests/test_missions.py
- [[complete_workout task is excluded on rest days.]] - rationale - tests/test_missions.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Rest_Day_Tasks_Test
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Nutrition Target Checks]]

## Top bridge nodes
- [[.test_omits_workout_task_on_rest_day()]] - degree 3, connects to 2 communities