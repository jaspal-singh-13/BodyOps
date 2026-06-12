"""
Low-level gspread helpers used by all services.

All operations target the Main Data Sheet via ``get_worksheet()``.
Row ordering follows the Google Sheets convention: row 1 is the header row,
row 2 is the first data row. All row indices in this module are 1-based.

Functions:
    read_rows        — return all records from a tab as a list of dicts.
    append_row       — append a new row in header-column order.
    append_rows_batch — append many rows in a single API call (avoids quota).
    update_row       — overwrite an existing row by 1-based row index.
    find_row         — find the first row matching a column/value filter.
    to_int / to_float — lenient cell parsers (blank/malformed → default).
    _col_letter      — convert a 1-based column number to a spreadsheet letter.
"""

import time
from typing import Any

import gspread

from ..logger import get_logger
from .sheets_client import get_or_create_worksheet, get_worksheet

logger = get_logger("sheets_repo")

# Per-tab header cache: populated on the first write to each tab and reused
# for all subsequent append_row / update_row calls, saving one row_values(1)
# round-trip per write operation.
_header_cache: dict[str, list[str]] = {}


def _get_headers(ws: gspread.Worksheet, tab: str) -> list[str]:
    """Return cached header row for the given tab, fetching once if needed."""
    if tab not in _header_cache:
        logger.debug("Sheets: header cache miss — fetching tab=%r", tab)
        _header_cache[tab] = ws.row_values(1)
        logger.debug("Sheets: headers cached tab=%r cols=%d", tab, len(_header_cache[tab]))
    return _header_cache[tab]


def to_int(value: Any, default: int = 0) -> int:
    """
    Return ``value`` as int, or ``default`` if it cannot be converted.

    ``get_all_records()`` returns ``""`` for blank cells, so a stray blank or
    partially-filled row must degrade to the default instead of raising and
    taking down every endpoint that reads the tab.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def to_float(value: Any, default: float = 0.0) -> float:
    """Return ``value`` as float, or ``default`` if it cannot be converted."""
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def read_rows(tab: str) -> list[dict[str, Any]]:
    """
    Return all data rows from a tab as a list of header-keyed dicts.

    Delegates to ``gspread.Worksheet.get_all_records()`` which uses row 1
    as the key names and returns rows 2+ as dicts.

    Args:
        tab: Tab name (e.g. ``"WeightLogs"``).

    Returns:
        List of dicts, one per data row. Empty list if no data rows exist.

    Raises:
        gspread.exceptions.WorksheetNotFound: If the tab does not exist.
    """
    t0 = time.perf_counter()
    rows = get_worksheet(tab).get_all_records()
    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.debug("Sheets read tab=%r rows=%d (%.0f ms)", tab, len(rows), elapsed_ms)
    return rows


def append_row(tab: str, row: dict[str, Any]) -> None:
    """
    Append a new row to a tab, writing values in header-column order.

    The header row is cached after the first call for each tab; subsequent
    appends to the same tab do not fetch the header again. Keys in ``row``
    that don't match any header are silently ignored. Missing keys result in
    an empty string in the corresponding cell.

    If the sheet is empty (no header row yet), the header row is written
    automatically from the dict keys before appending the first data row.

    Args:
        tab: Tab name (e.g. ``"WeightLogs"``).
        row: Dict mapping column header names to values.
    """
    ws = get_or_create_worksheet(tab)
    headers = _get_headers(ws, tab)
    if not headers:
        headers = list(row.keys())
        ws.append_row(headers, value_input_option="USER_ENTERED")
        _header_cache[tab] = headers
    values = [row.get(h, "") for h in headers]
    t0 = time.perf_counter()
    # USER_ENTERED lets Sheets parse dates/times as native values instead of
    # apostrophe-escaped text. Reads stay FORMATTED_VALUE so values round-trip
    # as the same strings that were written (e.g. "2026-06-12", "22:22").
    ws.append_row(values, value_input_option="USER_ENTERED")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.debug("Sheets append tab=%r (%.0f ms)", tab, elapsed_ms)


def append_rows_batch(tab: str, rows: list[dict[str, Any]]) -> None:
    """
    Append multiple rows to a tab in a single API call.

    Dramatically reduces quota consumption compared to calling ``append_row``
    in a loop — the entire batch counts as one write request instead of N.
    The header row is cached the same way as ``append_row``.

    Args:
        tab:  Tab name (e.g. ``"WorkoutPrograms"``).
        rows: List of dicts mapping column header names to values.
              An empty list is a no-op.
    """
    if not rows:
        return
    ws = get_or_create_worksheet(tab)
    headers = _get_headers(ws, tab)
    if not headers:
        headers = list(rows[0].keys())
        ws.append_row(headers, value_input_option="USER_ENTERED")
        _header_cache[tab] = headers
    values = [[row.get(h, "") for h in headers] for row in rows]
    t0 = time.perf_counter()
    ws.append_rows(values, value_input_option="USER_ENTERED")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.debug("Sheets batch-append tab=%r rows=%d (%.0f ms)", tab, len(rows), elapsed_ms)


def update_row(tab: str, row_index: int, row: dict[str, Any]) -> None:
    """
    Overwrite an existing row by 1-based row index.

    Row 1 is the header row, so the first data row is row 2. Values are
    written in header-column order; missing keys produce empty strings.
    The header row is cached — no extra round-trip per update.

    Args:
        tab: Tab name (e.g. ``"WeightLogs"``).
        row_index: 1-based row number to update (row 2 = first data row).
        row: Dict mapping column header names to new values.
    """
    ws = get_worksheet(tab)
    headers = _get_headers(ws, tab)
    values = [row.get(h, "") for h in headers]
    t0 = time.perf_counter()
    ws.update(f"A{row_index}:{_col_letter(len(headers))}{row_index}", [values], value_input_option="USER_ENTERED")
    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.debug("Sheets update tab=%r row=%d (%.0f ms)", tab, row_index, elapsed_ms)


def find_row(tab: str, column: str, value: str) -> tuple[int, dict[str, Any]] | None:
    """
    Return the first row matching a column/value filter.

    Both the stored value and ``value`` are cast to ``str`` before comparison
    so numeric sheet values (e.g. ``user_id``) match string queries.

    Args:
        tab: Tab name (e.g. ``"Settings"``).
        column: Header name of the column to search (e.g. ``"user_id"``).
        value: Value to match (compared as strings).

    Returns:
        ``(row_index, record)`` tuple where ``row_index`` is 1-based, or
        ``None`` if no matching row is found.
    """
    t0 = time.perf_counter()
    ws = get_worksheet(tab)
    records = ws.get_all_records()
    for i, record in enumerate(records):
        if str(record.get(column, "")) == str(value):
            elapsed_ms = (time.perf_counter() - t0) * 1000
            logger.debug("Sheets find tab=%r col=%r -> row %d (%.0f ms)", tab, column, i + 2, elapsed_ms)
            return i + 2, record  # +2: skip header row and convert to 1-based
    elapsed_ms = (time.perf_counter() - t0) * 1000
    logger.debug("Sheets find tab=%r col=%r -> not found (%.0f ms)", tab, column, elapsed_ms)
    return None


def _col_letter(n: int) -> str:
    """
    Convert a 1-based column number to a spreadsheet column letter.

    Examples: 1 → ``"A"``, 26 → ``"Z"``, 27 → ``"AA"``, 28 → ``"AB"``.

    Args:
        n: Column number (1-based).

    Returns:
        Column letter string.
    """
    result = ""
    while n:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result
