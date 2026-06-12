---
type: community
cohesion: 0.17
members: 21
---

# Weight Logging

**Cohesion:** 0.17 - loosely connected
**Members:** 21 nodes

## Members
- [[._validate_weight()_1]] - code - api/models/weight.py
- [[.test_appends_row_when_date_is_new()]] - code - tests/test_weight_service.py
- [[.test_fallback_time_uses_user_timezone()]] - code - tests/test_weight_service.py
- [[.test_invalid_timezone_falls_back_to_utc()]] - code - tests/test_weight_service.py
- [[.test_returns_correct_response_fields()]] - code - tests/test_weight_service.py
- [[.test_updates_row_when_date_already_logged()]] - code - tests/test_weight_service.py
- [[.test_worksheet_not_found_treats_as_empty()]] - code - tests/test_weight_service.py
- [[An unknown tz string must not crash — falls back to UTC.]] - rationale - tests/test_weight_service.py
- [[Request body for ``POST weight``.      Attributes         date Date of the]] - rationale - api/models/weight.py
- [[Return a callable that logs a weight entry for the given user.      The return]] - rationale - api/routers/agent.py
- [[TestLogWeight]] - code - tests/test_weight_service.py
- [[TestLogWeightTimezoneFallback]] - code - tests/test_weight_service.py
- [[Unit tests for weight_service upsert, history ordering, moving avg, projection.]] - rationale - tests/test_weight_service.py
- [[Upsert a weight entry append if the date+time is new, update if it exists.]] - rationale - api/services/weight_service.py
- [[WeightEntryCreate_2]] - code - api/services/weight_service.py
- [[WeightEntryCreate]] - code - api/models/weight.py
- [[WeightEntryResponse_2]] - code - api/services/weight_service.py
- [[When no time is supplied, the entry time is the current HHMM in tz_str.]] - rationale - tests/test_weight_service.py
- [[_make_weight_logger()]] - code - api/routers/agent.py
- [[log_weight()_1]] - code - api/services/weight_service.py
- [[test_weight_service.py]] - code - tests/test_weight_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Weight_Logging
SORT file.name ASC
```

## Connections to other communities
- 4 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 3 edges to [[_COMMUNITY_Weight Validation Models]]
- 3 edges to [[_COMMUNITY_Sheets Repo Helpers]]
- 3 edges to [[_COMMUNITY_Moving Average Computation]]
- 3 edges to [[_COMMUNITY_Weight History Logic]]
- 3 edges to [[_COMMUNITY_Goal Date Projection]]
- 2 edges to [[_COMMUNITY_Weight REST Endpoints]]
- 2 edges to [[_COMMUNITY_Workout Plan Management]]
- 1 edge to [[_COMMUNITY_Workout Models & Router Tests]]
- 1 edge to [[_COMMUNITY_Weight Models & Router Tests]]
- 1 edge to [[_COMMUNITY_Daily Task Service]]
- 1 edge to [[_COMMUNITY_Weight Trend Computation]]

## Top bridge nodes
- [[WeightEntryCreate]] - degree 22, connects to 8 communities
- [[log_weight()_1]] - degree 19, connects to 6 communities
- [[test_weight_service.py]] - degree 12, connects to 4 communities
- [[_make_weight_logger()]] - degree 5, connects to 1 community