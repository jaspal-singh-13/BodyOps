---
source_file: "api/services/weight_service.py"
type: "code"
community: "Weight History Logic"
location: "L102"
tags:
  - graphify/code
  - graphify/EXTRACTED
  - community/Weight_History_Logic
---

# get_history()

## Connections
- [[.test_change_kg_computed_correctly()]] - `calls` [EXTRACTED]
- [[.test_change_kg_none_for_oldest_entry()]] - `calls` [EXTRACTED]
- [[.test_empty_when_no_entries()]] - `calls` [EXTRACTED]
- [[.test_excludes_entries_older_than_90_days()]] - `calls` [EXTRACTED]
- [[.test_filters_to_current_user_only()]] - `calls` [EXTRACTED]
- [[.test_sorted_newest_first()]] - `calls` [EXTRACTED]
- [[.test_worksheet_not_found_returns_empty()]] - `calls` [EXTRACTED]
- [[Return the last 90 days of weight entries sorted newest first.      Computes `]] - `rationale_for` [EXTRACTED]
- [[WeightHistoryItem_2]] - `references` [EXTRACTED]
- [[WeightHistoryItem]] - `calls` [EXTRACTED]
- [[_parse_weight()]] - `calls` [EXTRACTED]
- [[read_rows()]] - `calls` [EXTRACTED]
- [[test_weight_service.py]] - `imports` [EXTRACTED]
- [[to_int()]] - `calls` [EXTRACTED]
- [[weight.py_1]] - `imports` [EXTRACTED]
- [[weight_service.py]] - `contains` [EXTRACTED]

#graphify/code #graphify/EXTRACTED #community/Weight_History_Logic