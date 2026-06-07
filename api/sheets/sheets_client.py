"""Singleton gspread client authenticated via service account."""
import json
import os

import gspread
from google.oauth2.service_account import Credentials

_client: gspread.Client | None = None

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]


def get_client() -> gspread.Client:
    global _client
    if _client is None:
        creds_json = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]
        creds_dict = json.loads(creds_json)
        creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
        _client = gspread.authorize(creds)
    return _client


def get_main_sheet() -> gspread.Spreadsheet:
    return get_client().open_by_key(os.environ["GOOGLE_SPREADSHEET_ID"])


def get_chat_history_sheet() -> gspread.Spreadsheet:
    return get_client().open_by_key(os.environ["GOOGLE_CHAT_HISTORY_SHEET_ID"])
