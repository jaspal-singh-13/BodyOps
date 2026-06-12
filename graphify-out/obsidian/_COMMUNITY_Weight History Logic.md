---
type: community
cohesion: 0.29
members: 13
---

# Weight History Logic

**Cohesion:** 0.29 - loosely connected
**Members:** 13 nodes

## Members
- [[._make_rows()]] - code - tests/test_weight_service.py
- [[.test_change_kg_computed_correctly()]] - code - tests/test_weight_service.py
- [[.test_change_kg_none_for_oldest_entry()]] - code - tests/test_weight_service.py
- [[.test_empty_when_no_entries()]] - code - tests/test_weight_service.py
- [[.test_excludes_entries_older_than_90_days()]] - code - tests/test_weight_service.py
- [[.test_filters_to_current_user_only()]] - code - tests/test_weight_service.py
- [[.test_sorted_newest_first()]] - code - tests/test_weight_service.py
- [[.test_worksheet_not_found_returns_empty()]] - code - tests/test_weight_service.py
- [[Build raw sheet rows from (user_id, date, weight_kg) tuples.]] - rationale - tests/test_weight_service.py
- [[Return the last 90 days of weight entries sorted newest first.      Computes `]] - rationale - api/services/weight_service.py
- [[TestGetHistory_1]] - code - tests/test_weight_service.py
- [[WeightHistoryItem_2]] - code - api/services/weight_service.py
- [[get_history()]] - code - api/services/weight_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Weight_History_Logic
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Weight Logging]]
- 1 edge to [[_COMMUNITY_Weight Models & Router Tests]]
- 1 edge to [[_COMMUNITY_Weight REST Endpoints]]
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]
- 1 edge to [[_COMMUNITY_Weight Trend Computation]]
- 1 edge to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Workout Plan Management]]

## Top bridge nodes
- [[get_history()]] - degree 16, connects to 7 communities
- [[TestGetHistory_1]] - degree 10, connects to 1 community