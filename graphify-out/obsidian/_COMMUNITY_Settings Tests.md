---
type: community
cohesion: 0.17
members: 12
---

# Settings Tests

**Cohesion:** 0.17 - loosely connected
**Members:** 12 nodes

## Members
- [[.test_get_settings_found()]] - code - tests/test_settings.py
- [[.test_get_settings_no_auth()]] - code - tests/test_settings.py
- [[.test_get_settings_not_found_empty_rows()]] - code - tests/test_settings.py
- [[.test_get_settings_not_found_wrong_user()]] - code - tests/test_settings.py
- [[.test_get_settings_worksheet_missing()]] - code - tests/test_settings.py
- [[.test_post_settings_creates_new()]] - code - tests/test_settings.py
- [[.test_post_settings_no_auth()]] - code - tests/test_settings.py
- [[.test_post_settings_updates_existing()]] - code - tests/test_settings.py
- [[TestGetSettings]] - code - tests/test_settings.py
- [[TestPostSettings]] - code - tests/test_settings.py
- [[Tests for GET settings and POST settings.]] - rationale - tests/test_settings.py
- [[test_settings.py]] - code - tests/test_settings.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Settings_Tests
SORT file.name ASC
```
