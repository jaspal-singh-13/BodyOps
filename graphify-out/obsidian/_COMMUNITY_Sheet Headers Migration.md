---
type: community
cohesion: 0.38
members: 7
---

# Sheet Headers Migration

**Cohesion:** 0.38 - loosely connected
**Members:** 7 nodes

## Members
- [[Client_4]] - code - scripts/migrate_sheet_headers.py
- [[One-time migration fix Google Sheet tabs whose header rows don't match the sch]] - rationale - scripts/migrate_sheet_headers.py
- [[Worksheet_5]] - code - scripts/migrate_sheet_headers.py
- [[get_client()_4]] - code - scripts/migrate_sheet_headers.py
- [[main()_4]] - code - scripts/migrate_sheet_headers.py
- [[migrate_sheet_headers.py]] - code - scripts/migrate_sheet_headers.py
- [[migrate_tab()_2]] - code - scripts/migrate_sheet_headers.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Sheet_Headers_Migration
SORT file.name ASC
```
