---
type: community
cohesion: 0.42
members: 9
---

# Moving Average Computation

**Cohesion:** 0.42 - moderately connected
**Members:** 9 nodes

## Members
- [[._entries()]] - code - tests/test_weight_service.py
- [[.test_first_six_entries_have_none_ma()]] - code - tests/test_weight_service.py
- [[.test_ma_correct_with_varying_weights()]] - code - tests/test_weight_service.py
- [[.test_seventh_entry_has_correct_ma()]] - code - tests/test_weight_service.py
- [[.test_single_entry_has_none_ma()]] - code - tests/test_weight_service.py
- [[Build dated weight entry dicts from a flat weight list.]] - rationale - tests/test_weight_service.py
- [[Compute a rolling moving average over a list of dated weight entries.      The]] - rationale - api/services/weight_service.py
- [[TestComputeMovingAvg]] - code - tests/test_weight_service.py
- [[_compute_moving_avg()]] - code - api/services/weight_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Moving_Average_Computation
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Weight Logging]]
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]
- 1 edge to [[_COMMUNITY_Weight Trend Computation]]

## Top bridge nodes
- [[_compute_moving_avg()]] - degree 8, connects to 3 communities
- [[TestComputeMovingAvg]] - degree 7, connects to 1 community