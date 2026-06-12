---
type: community
cohesion: 0.26
members: 13
---

# Plan ID Migration Script

**Cohesion:** 0.26 - loosely connected
**Members:** 13 nodes

## Members
- [[Client_1]] - code - scripts/migrate_add_plan_id.py
- [[One-time migration add plan_id support to workout tabs.  What this script doe]] - rationale - scripts/migrate_add_plan_id.py
- [[Return the program_name from the first WorkoutPrograms row for the user.]] - rationale - scripts/migrate_add_plan_id.py
- [[Return {user_id plan_id} for every distinct user_id found in WorkoutPrograms.]] - rationale - scripts/migrate_add_plan_id.py
- [[Spreadsheet_1]] - code - scripts/migrate_add_plan_id.py
- [[Worksheet_2]] - code - scripts/migrate_add_plan_id.py
- [[_collect_users()]] - code - scripts/migrate_add_plan_id.py
- [[_program_name_for_user()]] - code - scripts/migrate_add_plan_id.py
- [[ensure_plans_tab()]] - code - scripts/migrate_add_plan_id.py
- [[get_client()_1]] - code - scripts/migrate_add_plan_id.py
- [[main()_1]] - code - scripts/migrate_add_plan_id.py
- [[migrate_add_plan_id.py]] - code - scripts/migrate_add_plan_id.py
- [[migrate_tab()]] - code - scripts/migrate_add_plan_id.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Plan_ID_Migration_Script
SORT file.name ASC
```
