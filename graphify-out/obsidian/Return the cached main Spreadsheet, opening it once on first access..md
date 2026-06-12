---
source_file: "api/sheets/sheets_client.py"
type: "rationale"
community: "Sheets Client Singleton"
location: "L64"
tags:
  - graphify/rationale
  - graphify/EXTRACTED
  - community/Sheets_Client_Singleton
---

# Return the cached main Spreadsheet, opening it once on first access.

## Connections
- [[_get_spreadsheet()]] - `rationale_for` [EXTRACTED]

#graphify/rationale #graphify/EXTRACTED #community/Sheets_Client_Singleton