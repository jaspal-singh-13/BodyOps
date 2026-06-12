---
type: community
cohesion: 0.25
members: 8
---

# Settings Validation Models

**Cohesion:** 0.25 - loosely connected
**Members:** 8 nodes

## Members
- [[._validate_age()]] - code - api/models/settings.py
- [[._validate_height()]] - code - api/models/settings.py
- [[._validate_start_date()]] - code - api/models/settings.py
- [[._validate_targets()]] - code - api/models/settings.py
- [[._validate_wake_up_time()]] - code - api/models/settings.py
- [[._validate_weight()]] - code - api/models/settings.py
- [[Request body for ``POST settings`` (onboarding + updates).      Attributes]] - rationale - api/models/settings.py
- [[SettingsCreate]] - code - api/models/settings.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Settings_Validation_Models
SORT file.name ASC
```

## Connections to other communities
- 3 edges to [[_COMMUNITY_Settings Service & Router]]
- 1 edge to [[_COMMUNITY_Workout Models & Router Tests]]

## Top bridge nodes
- [[SettingsCreate]] - degree 11, connects to 2 communities