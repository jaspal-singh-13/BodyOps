---
type: community
cohesion: 0.40
members: 10
---

# Goal Date Projection

**Cohesion:** 0.40 - moderately connected
**Members:** 10 nodes

## Members
- [[._linear_entries()]] - code - tests/test_weight_service.py
- [[.test_correct_projection_simple_linear()]] - code - tests/test_weight_service.py
- [[.test_returns_none_when_too_far_future()]] - code - tests/test_weight_service.py
- [[.test_returns_none_when_trending_up()]] - code - tests/test_weight_service.py
- [[.test_returns_none_with_one_entry()]] - code - tests/test_weight_service.py
- [[.test_uses_last_14_when_more_available()]] - code - tests/test_weight_service.py
- [[Build entries that lose ``daily_loss`` kg each day from ``start_weight``.]] - rationale - tests/test_weight_service.py
- [[Project the date when the user will reach ``goal_weight_kg`` via OLS regression.]] - rationale - api/services/weight_service.py
- [[TestProjectGoalDate]] - code - tests/test_weight_service.py
- [[_project_goal_date()]] - code - api/services/weight_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Goal_Date_Projection
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Weight Logging]]
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]
- 1 edge to [[_COMMUNITY_Weight Trend Computation]]

## Top bridge nodes
- [[_project_goal_date()]] - degree 9, connects to 3 communities
- [[TestProjectGoalDate]] - degree 8, connects to 1 community