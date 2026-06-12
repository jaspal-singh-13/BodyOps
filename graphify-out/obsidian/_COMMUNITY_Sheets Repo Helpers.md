---
type: community
cohesion: 0.21
members: 13
---

# Sheets Repo Helpers

**Cohesion:** 0.21 - loosely connected
**Members:** 13 nodes

## Members
- [[Append a new row to a tab, writing values in header-column order.      The hea]] - rationale - api/sheets/sheets_repo.py
- [[Append multiple rows to a tab in a single API call.      Dramatically reduces]] - rationale - api/sheets/sheets_repo.py
- [[Business logic for weight tracking.  Reads from and writes to the ``WeightLogs]] - rationale - api/services/weight_service.py
- [[Convert a 1-based column number to a spreadsheet column letter.      Examples]] - rationale - api/sheets/sheets_repo.py
- [[Low-level gspread helpers used by all services.  All operations target the Mai]] - rationale - api/sheets/sheets_repo.py
- [[Return cached header row for the given tab, fetching once if needed.]] - rationale - api/sheets/sheets_repo.py
- [[Worksheet_1]] - code - api/sheets/sheets_repo.py
- [[_col_letter()]] - code - api/sheets/sheets_repo.py
- [[_get_headers()]] - code - api/sheets/sheets_repo.py
- [[append_row()]] - code - api/sheets/sheets_repo.py
- [[append_rows_batch()]] - code - api/sheets/sheets_repo.py
- [[sheets_repo.py]] - code - api/sheets/sheets_repo.py
- [[weight_service.py]] - code - api/services/weight_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Sheets_Repo_Helpers
SORT file.name ASC
```

## Connections to other communities
- 15 edges to [[_COMMUNITY_Workout Plan Management]]
- 8 edges to [[_COMMUNITY_Meal Service Logic]]
- 7 edges to [[_COMMUNITY_Daily Task Service]]
- 4 edges to [[_COMMUNITY_Logging Configuration]]
- 4 edges to [[_COMMUNITY_Settings Service & Router]]
- 3 edges to [[_COMMUNITY_Weight Logging]]
- 3 edges to [[_COMMUNITY_Weight Models & Router Tests]]
- 2 edges to [[_COMMUNITY_Weight Trend Computation]]
- 1 edge to [[_COMMUNITY_Weight Validation Models]]
- 1 edge to [[_COMMUNITY_Agent Router & Chat History]]
- 1 edge to [[_COMMUNITY_Weight REST Endpoints]]
- 1 edge to [[_COMMUNITY_Moving Average Computation]]
- 1 edge to [[_COMMUNITY_Weight History Logic]]
- 1 edge to [[_COMMUNITY_Goal Date Projection]]
- 1 edge to [[_COMMUNITY_Set Logging & Progression]]
- 1 edge to [[_COMMUNITY_Auth Sheet Credentials Cache]]
- 1 edge to [[_COMMUNITY_Sheets Client Singleton]]
- 1 edge to [[_COMMUNITY_Sheets Repo Tests]]

## Top bridge nodes
- [[weight_service.py]] - degree 21, connects to 12 communities
- [[sheets_repo.py]] - degree 21, connects to 8 communities
- [[append_row()]] - degree 16, connects to 6 communities
- [[append_rows_batch()]] - degree 14, connects to 3 communities
- [[_get_headers()]] - degree 6, connects to 1 community