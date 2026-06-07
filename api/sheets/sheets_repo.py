"""Low-level gspread helpers used by all services."""
from typing import Any

import gspread

from .sheets_client import get_main_sheet


def _tab(name: str) -> gspread.Worksheet:
    return get_main_sheet().worksheet(name)


def read_rows(tab: str) -> list[dict[str, Any]]:
    return _tab(tab).get_all_records()


def append_row(tab: str, row: dict[str, Any]) -> None:
    ws = _tab(tab)
    headers = ws.row_values(1)
    values = [row.get(h, "") for h in headers]
    ws.append_row(values, value_input_option="USER_ENTERED")


def update_row(tab: str, row_index: int, row: dict[str, Any]) -> None:
    """row_index is 1-based (row 1 = headers, row 2 = first data row)."""
    ws = _tab(tab)
    headers = ws.row_values(1)
    values = [row.get(h, "") for h in headers]
    ws.update(f"A{row_index}:{_col_letter(len(headers))}{row_index}", [values])


def find_row(tab: str, column: str, value: str) -> tuple[int, dict[str, Any]] | None:
    """Return (row_index, record) for the first matching row, or None."""
    ws = _tab(tab)
    records = ws.get_all_records()
    headers = ws.row_values(1)
    col_idx = headers.index(column) + 1  # 1-based
    for i, record in enumerate(records):
        if str(record.get(column, "")) == str(value):
            return i + 2, record  # +2: skip header row, convert to 1-based
    return None


def _col_letter(n: int) -> str:
    """Convert column number to letter (1→A, 26→Z, 27→AA)."""
    result = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result
