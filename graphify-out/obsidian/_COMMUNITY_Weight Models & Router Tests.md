---
type: community
cohesion: 0.13
members: 22
---

# Weight Models & Router Tests

**Cohesion:** 0.13 - loosely connected
**Members:** 22 nodes

## Members
- [[.test_get_history_empty_returns_empty_list()]] - code - tests/test_weight_router.py
- [[.test_get_history_no_auth_returns_401()]] - code - tests/test_weight_router.py
- [[.test_get_history_returns_list()]] - code - tests/test_weight_router.py
- [[.test_get_trend_no_auth_returns_401()]] - code - tests/test_weight_router.py
- [[.test_get_trend_no_settings_returns_404()]] - code - tests/test_weight_router.py
- [[.test_get_trend_returns_structure()]] - code - tests/test_weight_router.py
- [[.test_log_weight_invalid_weight_type_returns_422()]] - code - tests/test_weight_router.py
- [[.test_log_weight_missing_date_returns_422()]] - code - tests/test_weight_router.py
- [[.test_log_weight_missing_weight_returns_422()]] - code - tests/test_weight_router.py
- [[.test_log_weight_no_auth_returns_401()]] - code - tests/test_weight_router.py
- [[.test_log_weight_success()]] - code - tests/test_weight_router.py
- [[A single entry in the weight history list (GET weighthistory).      Attribut]] - rationale - api/models/weight.py
- [[Response returned after a successful weight log (POST weight).      Attribute]] - rationale - api/models/weight.py
- [[TestGetHistory]] - code - tests/test_weight_router.py
- [[TestGetTrend]] - code - tests/test_weight_router.py
- [[TestPostWeight]] - code - tests/test_weight_router.py
- [[Tests for POST weight, GET weighthistory, GET weighttrend.]] - rationale - tests/test_weight_router.py
- [[Trend analytics returned by GET weighttrend.      Attributes         movin]] - rationale - api/models/weight.py
- [[WeightEntryResponse]] - code - api/models/weight.py
- [[WeightHistoryItem]] - code - api/models/weight.py
- [[WeightTrendResponse]] - code - api/models/weight.py
- [[test_weight_router.py]] - code - tests/test_weight_router.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Weight_Models__Router_Tests
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Nutrition Target Checks]]
- 3 edges to [[_COMMUNITY_Workout Models & Router Tests]]
- 3 edges to [[_COMMUNITY_Weight Validation Models]]
- 3 edges to [[_COMMUNITY_Weight REST Endpoints]]
- 3 edges to [[_COMMUNITY_Sheets Repo Helpers]]
- 1 edge to [[_COMMUNITY_Weight Logging]]
- 1 edge to [[_COMMUNITY_Weight History Logic]]
- 1 edge to [[_COMMUNITY_Weight Trend Computation]]

## Top bridge nodes
- [[WeightEntryResponse]] - degree 10, connects to 5 communities
- [[WeightHistoryItem]] - degree 10, connects to 5 communities
- [[WeightTrendResponse]] - degree 10, connects to 5 communities
- [[TestPostWeight]] - degree 10, connects to 1 community
- [[test_weight_router.py]] - degree 8, connects to 1 community