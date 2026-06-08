"""
Unit tests for api/sheets/sheets_repo.py — all gspread calls are mocked.

Every test class patches ``get_main_sheet`` at the repo module level so no
real network calls are made. The ``_make_ws`` helper creates a pre-configured
``MagicMock`` worksheet to keep test setup concise.
"""

from unittest.mock import MagicMock, patch

import pytest

from api.sheets import sheets_repo


def _make_ws(headers: list[str], records: list[dict]) -> MagicMock:
    """
    Build a mock ``gspread.Worksheet`` with preset headers and records.

    Args:
        headers: Column names returned by ``ws.row_values(1)``.
        records: Dicts returned by ``ws.get_all_records()``.

    Returns:
        Configured ``MagicMock`` that behaves like a ``gspread.Worksheet``.
    """
    ws = MagicMock()
    ws.row_values.return_value = headers
    ws.get_all_records.return_value = records
    return ws


@patch("api.sheets.sheets_repo.get_worksheet")
class TestReadRows:
    def test_returns_all_records(self, mock_get_ws):
        records = [{"id": "1", "date": "2026-01-01", "weight_kg": "80"}]
        mock_get_ws.return_value.get_all_records.return_value = records

        result = sheets_repo.read_rows("WeightLogs")

        assert result == records

    def test_returns_empty_list_when_no_data(self, mock_get_ws):
        mock_get_ws.return_value.get_all_records.return_value = []

        result = sheets_repo.read_rows("WeightLogs")

        assert result == []


@patch("api.sheets.sheets_repo.get_worksheet")
class TestAppendRow:
    def setup_method(self):
        sheets_repo._header_cache.clear()

    def test_appends_values_in_header_order(self, mock_get_ws):
        ws = _make_ws(["id", "date", "weight_kg"], [])
        mock_get_ws.return_value = ws

        sheets_repo.append_row("WeightLogs", {"date": "2026-01-01", "id": "abc", "weight_kg": "80"})

        ws.append_row.assert_called_once_with(
            ["abc", "2026-01-01", "80"], value_input_option="USER_ENTERED"
        )

    def test_missing_keys_fill_with_empty_string(self, mock_get_ws):
        ws = _make_ws(["id", "date", "weight_kg"], [])
        mock_get_ws.return_value = ws

        sheets_repo.append_row("WeightLogs", {"id": "abc"})

        ws.append_row.assert_called_once_with(["abc", "", ""], value_input_option="USER_ENTERED")


@patch("api.sheets.sheets_repo.get_worksheet")
class TestUpdateRow:
    def test_updates_correct_range(self, mock_get_ws):
        ws = _make_ws(["id", "date", "weight_kg"], [])
        mock_get_ws.return_value = ws

        sheets_repo.update_row("WeightLogs", 2, {"id": "abc", "date": "2026-01-01", "weight_kg": "82"})

        ws.update.assert_called_once_with("A2:C2", [["abc", "2026-01-01", "82"]])

    def test_missing_keys_fill_with_empty_string(self, mock_get_ws):
        ws = _make_ws(["id", "date", "weight_kg"], [])
        mock_get_ws.return_value = ws

        sheets_repo.update_row("WeightLogs", 3, {"id": "xyz"})

        ws.update.assert_called_once_with("A3:C3", [["xyz", "", ""]])


@patch("api.sheets.sheets_repo.get_worksheet")
class TestFindRow:
    def test_returns_row_index_and_record_when_found(self, mock_get_ws):
        records = [
            {"id": "1", "date": "2026-01-01"},
            {"id": "2", "date": "2026-01-02"},
        ]
        ws = _make_ws(["id", "date"], records)
        mock_get_ws.return_value = ws

        result = sheets_repo.find_row("WeightLogs", "id", "2")

        assert result == (3, {"id": "2", "date": "2026-01-02"})

    def test_returns_none_when_not_found(self, mock_get_ws):
        ws = _make_ws(["id", "date"], [{"id": "1", "date": "2026-01-01"}])
        mock_get_ws.return_value = ws

        result = sheets_repo.find_row("WeightLogs", "id", "999")

        assert result is None

    def test_returns_first_match_when_duplicates(self, mock_get_ws):
        records = [
            {"id": "1", "date": "2026-01-01"},
            {"id": "1", "date": "2026-01-02"},
        ]
        ws = _make_ws(["id", "date"], records)
        mock_get_ws.return_value = ws

        result = sheets_repo.find_row("WeightLogs", "id", "1")

        assert result == (2, {"id": "1", "date": "2026-01-01"})


class TestColLetter:
    def test_single_letters(self):
        assert sheets_repo._col_letter(1) == "A"
        assert sheets_repo._col_letter(26) == "Z"

    def test_double_letters(self):
        assert sheets_repo._col_letter(27) == "AA"
        assert sheets_repo._col_letter(28) == "AB"
