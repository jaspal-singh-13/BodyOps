---
type: community
cohesion: 0.21
members: 13
---

# Auth Sheet Credentials Cache

**Cohesion:** 0.21 - loosely connected
**Members:** 13 nodes

## Members
- [[Background asyncio task re-sync credentials whenever the Auth Sheet changes.]] - rationale - api/sheets/auth_sheet.py
- [[Credentials cache backed by the Auth Sheet.  On startup ``load_credentials()``]] - rationale - api/sheets/auth_sheet.py
- [[Fetch all credential rows from the Auth Sheet (synchronous).]] - rationale - api/sheets/auth_sheet.py
- [[Fetch credentials from the Auth Sheet and populate the in-memory cache.      C]] - rationale - api/sheets/auth_sheet.py
- [[Return all cached credential rows — pure in-memory lookup, no IO.      Raises]] - rationale - api/sheets/auth_sheet.py
- [[Return the credential row matching ``email`` (case-insensitive), or None.]] - rationale - api/sheets/auth_sheet.py
- [[_fetch_from_sheet()]] - code - api/sheets/auth_sheet.py
- [[_set_credentials()]] - code - api/sheets/auth_sheet.py
- [[auth_sheet.py]] - code - api/sheets/auth_sheet.py
- [[find_user()]] - code - api/sheets/auth_sheet.py
- [[get_credentials()]] - code - api/sheets/auth_sheet.py
- [[load_credentials()]] - code - api/sheets/auth_sheet.py
- [[poll_credentials()]] - code - api/sheets/auth_sheet.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Auth_Sheet_Credentials_Cache
SORT file.name ASC
```

## Connections to other communities
- 7 edges to [[_COMMUNITY_App Entry & Login]]
- 3 edges to [[_COMMUNITY_Sheets Client Singleton]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 2 edges to [[_COMMUNITY_Workout Plan Management]]
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]

## Top bridge nodes
- [[auth_sheet.py]] - degree 15, connects to 5 communities
- [[_fetch_from_sheet()]] - degree 5, connects to 2 communities
- [[find_user()]] - degree 5, connects to 1 community
- [[load_credentials()]] - degree 5, connects to 1 community
- [[poll_credentials()]] - degree 5, connects to 1 community