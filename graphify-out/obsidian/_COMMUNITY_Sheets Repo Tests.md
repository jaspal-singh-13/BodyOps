---
type: community
cohesion: 0.09
members: 28
---

# Sheets Repo Tests

**Cohesion:** 0.09 - loosely connected
**Members:** 28 nodes

## Members
- [[.setup_method()]] - code - tests/test_sheets_repo.py
- [[.test_appends_values_in_header_order()]] - code - tests/test_sheets_repo.py
- [[.test_double_letters()]] - code - tests/test_sheets_repo.py
- [[.test_missing_keys_fill_with_empty_string()]] - code - tests/test_sheets_repo.py
- [[.test_missing_keys_fill_with_empty_string()_1]] - code - tests/test_sheets_repo.py
- [[.test_returns_all_records()]] - code - tests/test_sheets_repo.py
- [[.test_returns_empty_list_when_no_data()]] - code - tests/test_sheets_repo.py
- [[.test_returns_first_match_when_duplicates()]] - code - tests/test_sheets_repo.py
- [[.test_returns_none_when_not_found()]] - code - tests/test_sheets_repo.py
- [[.test_returns_row_index_and_record_when_found()]] - code - tests/test_sheets_repo.py
- [[.test_single_letters()]] - code - tests/test_sheets_repo.py
- [[.test_to_float_blank_or_garbage_returns_default()]] - code - tests/test_sheets_repo.py
- [[.test_to_float_parses_numbers_and_numeric_strings()]] - code - tests/test_sheets_repo.py
- [[.test_to_int_blank_cell_returns_default()]] - code - tests/test_sheets_repo.py
- [[.test_to_int_garbage_returns_default()]] - code - tests/test_sheets_repo.py
- [[.test_to_int_parses_numbers_and_numeric_strings()]] - code - tests/test_sheets_repo.py
- [[.test_updates_correct_range()]] - code - tests/test_sheets_repo.py
- [[Build a mock ``gspread.Worksheet`` with preset headers and records.      Args]] - rationale - tests/test_sheets_repo.py
- [[TestAppendRow]] - code - tests/test_sheets_repo.py
- [[TestColLetter]] - code - tests/test_sheets_repo.py
- [[TestFindRow]] - code - tests/test_sheets_repo.py
- [[TestReadRows]] - code - tests/test_sheets_repo.py
- [[TestToIntToFloat]] - code - tests/test_sheets_repo.py
- [[TestUpdateRow]] - code - tests/test_sheets_repo.py
- [[Unit tests for apisheetssheets_repo.py — all gspread calls are mocked.  Ever]] - rationale - tests/test_sheets_repo.py
- [[_make_ws()]] - code - tests/test_sheets_repo.py
- [[test_sheets_repo.py]] - code - tests/test_sheets_repo.py
- [[to_int  to_float degrade blank or malformed cells to the default.]] - rationale - tests/test_sheets_repo.py

## Live Query (requires Dataview plugin)

```dataview
TABLE source_file, type FROM #community/Sheets_Repo_Tests
SORT file.name ASC
```

## Connections to other communities
- 1 edge to [[_COMMUNITY_Sheets Repo Helpers]]

## Top bridge nodes
- [[test_sheets_repo.py]] - degree 9, connects to 1 community