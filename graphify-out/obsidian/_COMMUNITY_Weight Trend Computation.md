---
type: community
cohesion: 0.33
members: 6
---

# Weight Trend Computation

**Cohesion:** 0.33 - loosely connected
**Members:** 6 nodes

## Members
- [[Any]] - code - api/services/weight_service.py
- [[Compute the 7-day moving average and a linear-regression goal projection.]] - rationale - api/services/weight_service.py
- [[Return ``value`` as float, or ``None`` if it cannot be converted.      Guards]] - rationale - api/services/weight_service.py
- [[WeightTrendResponse_2]] - code - api/services/weight_service.py
- [[_parse_weight()]] - code - api/services/weight_service.py
- [[get_trend()]] - code - api/services/weight_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Weight_Trend_Computation
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 2 edges to [[_COMMUNITY_Sheets Repo Helpers]]
- 1 edge to [[_COMMUNITY_Weight Models & Router Tests]]
- 1 edge to [[_COMMUNITY_Weight REST Endpoints]]
- 1 edge to [[_COMMUNITY_Weight History Logic]]
- 1 edge to [[_COMMUNITY_Moving Average Computation]]
- 1 edge to [[_COMMUNITY_Goal Date Projection]]
- 1 edge to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Workout Plan Management]]
- 1 edge to [[_COMMUNITY_Weight Logging]]

## Top bridge nodes
- [[get_trend()]] - degree 13, connects to 9 communities
- [[_parse_weight()]] - degree 5, connects to 2 communities