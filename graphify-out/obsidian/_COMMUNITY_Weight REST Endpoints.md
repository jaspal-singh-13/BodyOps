---
type: community
cohesion: 0.23
members: 16
---

# Weight REST Endpoints

**Cohesion:** 0.23 - loosely connected
**Members:** 16 nodes

## Members
- [[Fire-and-forget wrapper so task completion never delays the response.]] - rationale - api/routers/weight.py
- [[Log a body weight entry, updating if an entry already exists for that date.]] - rationale - api/routers/weight.py
- [[Return 7-day moving average and linear-regression goal projection.      Fetche]] - rationale - api/routers/weight.py
- [[Return the last 90 days of weight entries for the authenticated user.      Ent]] - rationale - api/routers/weight.py
- [[Run a coroutine as a background task that survives garbage collection._1]] - rationale - api/routers/weight.py
- [[Weight router — daily weigh-in logging and trend analytics.  Endpoints     P]] - rationale - api/routers/weight.py
- [[WeightEntryCreate_1]] - code - api/routers/weight.py
- [[WeightEntryResponse_1]] - code - api/routers/weight.py
- [[WeightHistoryItem_1]] - code - api/routers/weight.py
- [[WeightTrendResponse_1]] - code - api/routers/weight.py
- [[_bg_auto_complete()]] - code - api/routers/weight.py
- [[_spawn_bg()_1]] - code - api/routers/weight.py
- [[get_history_endpoint()_1]] - code - api/routers/weight.py
- [[get_trend_endpoint()]] - code - api/routers/weight.py
- [[log_weight_endpoint()]] - code - api/routers/weight.py
- [[weight.py_1]] - code - api/routers/weight.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Weight_REST_Endpoints
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_App Entry & Login]]
- 3 edges to [[_COMMUNITY_Weight Models & Router Tests]]
- 2 edges to [[_COMMUNITY_Weight Logging]]
- 2 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 2 edges to [[_COMMUNITY_Settings Service & Router]]
- 2 edges to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Meals Router & Auth Dependency]]
- 1 edge to [[_COMMUNITY_Weight Validation Models]]
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]
- 1 edge to [[_COMMUNITY_Weight History Logic]]
- 1 edge to [[_COMMUNITY_Weight Trend Computation]]

## Top bridge nodes
- [[weight.py_1]] - degree 23, connects to 10 communities
- [[WeightEntryCreate_1]] - degree 8, connects to 1 community