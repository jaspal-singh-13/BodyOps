---
type: community
cohesion: 1.00
members: 2
---

# Workout Day Tasks Test

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[.test_returns_all_tasks_for_workout_day()]] - code - tests/test_missions.py
- [[Returns 5 tasks when today is a workout day.]] - rationale - tests/test_missions.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Workout_Day_Tasks_Test
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Nutrition Target Checks]]

## Top bridge nodes
- [[.test_returns_all_tasks_for_workout_day()]] - degree 3, connects to 2 communities