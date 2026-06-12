---
type: community
cohesion: 0.53
members: 6
---

# Settings Endpoints

**Cohesion:** 0.53 - moderately connected
**Members:** 6 nodes

## Members
- [[Create or update the authenticated user's settings row (upsert).      The serv]] - rationale - api/routers/settings.py
- [[Return the authenticated user's settings row.      Used by the frontend on eve]] - rationale - api/routers/settings.py
- [[SettingsCreate_1]] - code - api/routers/settings.py
- [[SettingsResponse_1]] - code - api/routers/settings.py
- [[get_settings_endpoint()]] - code - api/routers/settings.py
- [[save_settings_endpoint()]] - code - api/routers/settings.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Settings_Endpoints
SORT file.name ASC
```

## Connections to other communities
- 2 edges to [[_COMMUNITY_Settings Service & Router]]

## Top bridge nodes
- [[save_settings_endpoint()]] - degree 4, connects to 1 community
- [[get_settings_endpoint()]] - degree 3, connects to 1 community