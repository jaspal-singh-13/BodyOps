---
type: community
cohesion: 0.38
members: 7
---

# Weight Time Migration

**Cohesion:** 0.38 - loosely connected
**Members:** 7 nodes

## Members
- [[Client_3]] - code - scripts/migrate_add_weight_time.py
- [[Migration add ``time`` column to the WeightLogs tab after ``date``.  Safe to ru]] - rationale - scripts/migrate_add_weight_time.py
- [[Worksheet_4]] - code - scripts/migrate_add_weight_time.py
- [[get_client()_3]] - code - scripts/migrate_add_weight_time.py
- [[main()_3]] - code - scripts/migrate_add_weight_time.py
- [[migrate()]] - code - scripts/migrate_add_weight_time.py
- [[migrate_add_weight_time.py]] - code - scripts/migrate_add_weight_time.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Weight_Time_Migration
SORT file.name ASC
```
