---
type: community
cohesion: 0.24
members: 10
---

# User ID Migration Script

**Cohesion:** 0.24 - loosely connected
**Members:** 10 nodes

## Members
- [[Build and return an authenticated gspread client.      Returns         Autho]] - rationale - scripts/migrate_add_user_id.py
- [[Client_2]] - code - scripts/migrate_add_user_id.py
- [[Entry point connect to Sheets and migrate all applicable tabs.      Tabs that]] - rationale - scripts/migrate_add_user_id.py
- [[Insert ``user_id`` as column A if not already present.      If the sheet is em]] - rationale - scripts/migrate_add_user_id.py
- [[Migration add user_id as the first column to all Main Data Sheet tabs.  Safe]] - rationale - scripts/migrate_add_user_id.py
- [[Worksheet_3]] - code - scripts/migrate_add_user_id.py
- [[get_client()_2]] - code - scripts/migrate_add_user_id.py
- [[main()_2]] - code - scripts/migrate_add_user_id.py
- [[migrate_add_user_id.py]] - code - scripts/migrate_add_user_id.py
- [[migrate_tab()_1]] - code - scripts/migrate_add_user_id.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/User_ID_Migration_Script
SORT file.name ASC
```
