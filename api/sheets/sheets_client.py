"""
Singleton gspread client authenticated via service account.

A single ``gspread.Client`` instance is reused across the process lifetime to
avoid re-authenticating on every request. The client is initialised lazily on
the first call to ``get_client()``.

Required env vars:
    GOOGLE_SERVICE_ACCOUNT_JSON  — full service account JSON as a string.
    GOOGLE_SPREADSHEET_ID        — ID of the Main Data Sheet.
    GOOGLE_CHAT_HISTORY_SHEET_ID — ID of the Chat History Sheet.
"""

import json
import os

import gspread
from google.oauth2.service_account import Credentials

# Module-level singleton — initialised on first call to get_client()
_client: gspread.Client | None = None

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
    return _client


def get_main_sheet() -> gspread.Spreadsheet:
    """
    Open and return the Main Data Sheet spreadsheet.

    The Main Data Sheet contains all app tabs: WeightLogs, Settings, Meals, etc.

    Returns:
        ``gspread.Spreadsheet`` for the Main Data Sheet.

    Raises:
        KeyError: If ``GOOGLE_SPREADSHEET_ID`` is not set.
        gspread.exceptions.SpreadsheetNotFound: If the ID is invalid or the
            service account does not have access.
    """
    return get_client().open_by_key(os.environ["GOOGLE_SPREADSHEET_ID"])


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
