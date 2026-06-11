"""
Singleton gspread client authenticated via service account.

A single ``gspread.Client`` instance is reused across the process lifetime to
avoid re-authenticating on every request. The client is initialised lazily on
the first call to ``get_client()``.

The main spreadsheet object and individual ``Worksheet`` handles are also
cached so that repeated operations on the same tab do not pay the cost of
``open_by_key`` + ``worksheet()`` on every call.

Required env vars:
    GOOGLE_SERVICE_ACCOUNT_JSON  — full service account JSON as a string.
    GOOGLE_SPREADSHEET_ID        — ID of the Main Data Sheet.
    GOOGLE_CHAT_HISTORY_SHEET_ID — ID of the Chat History Sheet.
"""

import json
import os

import gspread
from google.oauth2.service_account import Credentials

from ..logger import get_logger

logger = get_logger("sheets_client")

# Module-level singletons
_client: gspread.Client | None = None
_spreadsheet: gspread.Spreadsheet | None = None
_worksheet_cache: dict[str, gspread.Worksheet] = {}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client() -> gspread.Client:
    """
    Return the shared gspread client, initialising it on first call.

    Reads ``GOOGLE_SERVICE_ACCOUNT_JSON`` from the environment and parses it
    as JSON. The same client instance is reused for all subsequent calls.

    Returns:
        Authenticated ``gspread.Client`` instance.

    Raises:
        KeyError: If ``GOOGLE_SERVICE_ACCOUNT_JSON`` is not set.
        json.JSONDecodeError: If the env var value is not valid JSON.
    """
    global _client
    if _client is None:
        creds_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        _client = gspread.authorize(creds)
        logger.info("Sheets client: authorized (service_account=%s)", creds_dict.get("client_email", "?"))
    return _client


def _get_spreadsheet() -> gspread.Spreadsheet:
    """Return the cached main Spreadsheet, opening it once on first access."""
    global _spreadsheet
    if _spreadsheet is None:
        sheet_id = os.environ["GOOGLE_SPREADSHEET_ID"]
        _spreadsheet = get_client().open_by_key(sheet_id)
        logger.info("Sheets: opened main spreadsheet id=%s title=%r", sheet_id, _spreadsheet.title)
    return _spreadsheet


def get_main_sheet() -> gspread.Spreadsheet:
    """
    Open and return the Main Data Sheet spreadsheet.

    The Main Data Sheet contains all app tabs: WeightLogs, Settings, Meals, etc.
    The ``Spreadsheet`` object is cached after the first call — subsequent calls
    return the same instance without an additional ``open_by_key`` round-trip.

    Returns:
        ``gspread.Spreadsheet`` for the Main Data Sheet.

    Raises:
        KeyError: If ``GOOGLE_SPREADSHEET_ID`` is not set.
        gspread.exceptions.SpreadsheetNotFound: If the ID is invalid or the
            service account does not have access.
    """
    return _get_spreadsheet()


def get_worksheet(name: str) -> gspread.Worksheet:
    """
    Return a cached ``Worksheet`` handle for the given tab name.

    On the first call for a given ``name``, opens the worksheet via the
    Sheets API and stores it in a module-level dict.  All subsequent calls
    return the cached object instantly — no HTTP round-trip.

    Args:
        name: Tab name as it appears in the spreadsheet (e.g. ``"WeightLogs"``).

    Returns:
        Cached ``gspread.Worksheet`` instance.

    Raises:
        gspread.exceptions.WorksheetNotFound: If no tab with that name exists.
    """
    if name not in _worksheet_cache:
        logger.debug("Sheets: worksheet cache miss — opening tab=%r", name)
        _worksheet_cache[name] = _get_spreadsheet().worksheet(name)
        logger.info("Sheets: worksheet tab=%r opened and cached", name)
    return _worksheet_cache[name]


def get_chat_history_sheet() -> gspread.Spreadsheet:
    """
    Open and return the Chat History Sheet spreadsheet.

    Contains the ``ChatHistory`` tab used for persisting agent conversation
    history across process restarts (future phase).

    Returns:
        ``gspread.Spreadsheet`` for the Chat History Sheet.

    Raises:
        KeyError: If ``GOOGLE_CHAT_HISTORY_SHEET_ID`` is not set.
    """
    return get_client().open_by_key(os.environ["GOOGLE_CHAT_HISTORY_SHEET_ID"])
