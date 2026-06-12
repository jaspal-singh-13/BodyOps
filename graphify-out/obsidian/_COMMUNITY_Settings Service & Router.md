---
type: community
cohesion: 0.12
members: 26
---

# Settings Service & Router

**Cohesion:** 0.12 - loosely connected
**Members:** 26 nodes

## Members
- [[Business logic for user settings.  Reads from and writes to the ``Settings`` t]] - rationale - api/services/settings_service.py
- [[Fetch the settings row for a user from the ``Settings`` sheet tab.      Result]] - rationale - api/services/settings_service.py
- [[Persist the user's reminder configuration to the ``reminders_json`` field.]] - rationale - api/services/settings_service.py
- [[Pydantic models for user settings.  Settings are scoped to a single user (``us]] - rationale - api/models/settings.py
- [[Return (hit, value). hit is True only when the entry is within TTL.]] - rationale - api/services/settings_service.py
- [[Return the authenticated user's reminder configuration.      Returns]] - rationale - api/routers/settings.py
- [[Return the first row matching a columnvalue filter.      Both the stored valu]] - rationale - api/sheets/sheets_repo.py
- [[Return the user's reminder configuration as a parsed dict.      Reads ``remind]] - rationale - api/services/settings_service.py
- [[Save the authenticated user's reminder configuration.      The entire reminder]] - rationale - api/routers/settings.py
- [[Settings router — user profile and onboarding data.  Endpoints     GET  set]] - rationale - api/routers/settings.py
- [[SettingsCreate_2]] - code - api/services/settings_service.py
- [[SettingsResponse_2]] - code - api/services/settings_service.py
- [[Upsert the settings row for a user update if found, append if not.      Stamp]] - rationale - api/services/settings_service.py
- [[_cache_get()]] - code - api/services/settings_service.py
- [[_cache_invalidate()]] - code - api/services/settings_service.py
- [[_cache_set()]] - code - api/services/settings_service.py
- [[find_row()]] - code - api/sheets/sheets_repo.py
- [[get_reminders()]] - code - api/services/settings_service.py
- [[get_reminders_endpoint()]] - code - api/routers/settings.py
- [[get_settings()]] - code - api/services/settings_service.py
- [[save_reminders()]] - code - api/services/settings_service.py
- [[save_reminders_endpoint()]] - code - api/routers/settings.py
- [[save_settings()]] - code - api/services/settings_service.py
- [[settings.py]] - code - api/models/settings.py
- [[settings.py_1]] - code - api/routers/settings.py
- [[settings_service.py]] - code - api/services/settings_service.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Settings_Service__Router
SORT file.name ASC
```

## Connections to other communities
- 6 edges to [[_COMMUNITY_Nutrition Target Checks]]
- 6 edges to [[_COMMUNITY_Meal Service Logic]]
- 6 edges to [[_COMMUNITY_Workout Plan Management]]
- 4 edges to [[_COMMUNITY_Sheets Repo Helpers]]
- 3 edges to [[_COMMUNITY_App Entry & Login]]
- 3 edges to [[_COMMUNITY_Settings Validation Models]]
- 3 edges to [[_COMMUNITY_Agent Router & Chat History]]
- 3 edges to [[_COMMUNITY_Daily Task Service]]
- 2 edges to [[_COMMUNITY_Logging Configuration]]
- 2 edges to [[_COMMUNITY_Settings Endpoints]]
- 2 edges to [[_COMMUNITY_Weight REST Endpoints]]
- 1 edge to [[_COMMUNITY_Meals Router & Auth Dependency]]

## Top bridge nodes
- [[settings_service.py]] - degree 24, connects to 9 communities
- [[get_settings()]] - degree 18, connects to 6 communities
- [[settings.py_1]] - degree 17, connects to 5 communities
- [[save_settings()]] - degree 10, connects to 3 communities
- [[find_row()]] - degree 7, connects to 3 communities