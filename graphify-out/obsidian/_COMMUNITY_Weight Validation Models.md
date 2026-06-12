---
type: community
cohesion: 0.33
members: 6
---

# Weight Validation Models

**Cohesion:** 0.33 - loosely connected
**Members:** 6 nodes

## Members
- [[._validate_date()_3]] - code - api/models/weight.py
- [[._validate_time()_1]] - code - api/models/weight.py
- [[Pydantic models for weight tracking.  Data flow     POST weight  → WeightEn]] - rationale - api/models/weight.py
- [[_check_date()]] - code - api/models/weight.py
- [[_check_time()]] - code - api/models/weight.py
- [[weight.py]] - code - api/models/weight.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Weight_Validation_Models
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Weight Logging]]
- 3 edges to [[_COMMUNITY_Weight Models & Router Tests]]
- 1 edge to [[_COMMUNITY_Agent Router & Chat History]]
- 1 edge to [[_COMMUNITY_Weight REST Endpoints]]
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]

## Top bridge nodes
- [[weight.py]] - degree 10, connects to 5 communities
- [[._validate_date()_3]] - degree 2, connects to 1 community
- [[._validate_time()_1]] - degree 2, connects to 1 community