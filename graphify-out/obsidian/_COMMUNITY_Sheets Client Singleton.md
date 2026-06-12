---
type: community
cohesion: 0.24
members: 12
---

# Sheets Client Singleton

**Cohesion:** 0.24 - loosely connected
**Members:** 12 nodes

## Members
- [[Client]] - code - api/sheets/sheets_client.py
- [[Open and return the Chat History Sheet spreadsheet.      Contains the ``ChatHi]] - rationale - api/sheets/sheets_client.py
- [[Open and return the Main Data Sheet spreadsheet.      The Main Data Sheet cont]] - rationale - api/sheets/sheets_client.py
- [[Return the cached main Spreadsheet, opening it once on first access.]] - rationale - api/sheets/sheets_client.py
- [[Return the shared gspread client, initialising it on first call.      Reads ``]] - rationale - api/sheets/sheets_client.py
- [[Singleton gspread client authenticated via service account.  A single ``gsprea]] - rationale - api/sheets/sheets_client.py
- [[Spreadsheet]] - code - api/sheets/sheets_client.py
- [[_get_spreadsheet()]] - code - api/sheets/sheets_client.py
- [[get_chat_history_sheet()]] - code - api/sheets/sheets_client.py
- [[get_client()]] - code - api/sheets/sheets_client.py
- [[get_main_sheet()]] - code - api/sheets/sheets_client.py
- [[sheets_client.py]] - code - api/sheets/sheets_client.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Sheets_Client_Singleton
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_App Entry & Login]]
- 3 edges to [[_COMMUNITY_Workout Plan Management]]
- 3 edges to [[_COMMUNITY_Auth Sheet Credentials Cache]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]

## Top bridge nodes
- [[sheets_client.py]] - degree 12, connects to 5 communities
- [[get_client()]] - degree 7, connects to 1 community
- [[get_main_sheet()]] - degree 6, connects to 1 community
- [[_get_spreadsheet()]] - degree 6, connects to 1 community