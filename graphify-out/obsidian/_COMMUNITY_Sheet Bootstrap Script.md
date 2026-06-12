---
type: community
cohesion: 0.21
members: 12
---

# Sheet Bootstrap Script

**Cohesion:** 0.21 - loosely connected
**Members:** 12 nodes

## Members
- [[Bootstrap all Google Sheet tabs. Safe to run multiple times — idempotent.  Wha]] - rationale - scripts/setup.py
- [[Build and return an authenticated gspread client.      Reads ``GOOGLE_SERVICE_]] - rationale - scripts/setup.py
- [[Check all required env vars are present; exit with code 1 if any are missing.]] - rationale - scripts/setup.py
- [[Client_5]] - code - scripts/setup.py
- [[Create missing tabs in a spreadsheet and write their header rows.      For exi]] - rationale - scripts/setup.py
- [[Entry point validate env, connect to Sheets, and bootstrap all tabs.      Exi]] - rationale - scripts/setup.py
- [[Spreadsheet_2]] - code - scripts/setup.py
- [[ensure_tabs()]] - code - scripts/setup.py
- [[get_client()_5]] - code - scripts/setup.py
- [[main()_5]] - code - scripts/setup.py
- [[setup.py]] - code - scripts/setup.py
- [[validate_env()]] - code - scripts/setup.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Sheet_Bootstrap_Script
SORT file.name ASC
```
