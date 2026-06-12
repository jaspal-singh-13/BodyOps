---
type: community
cohesion: 1.00
members: 2
---

# Status Totals Test

**Cohesion:** 1.00 - tightly connected
**Members:** 2 nodes

## Members
- [[.test_returns_correct_totals()]] - code - tests/test_missions.py
- [[get_status returns correct total, completed, and percentage fields.]] - rationale - tests/test_missions.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Status_Totals_Test
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Nutrition Target Checks]]

## Top bridge nodes
- [[.test_returns_correct_totals()]] - degree 3, connects to 2 communities