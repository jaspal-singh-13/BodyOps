"""Read credentials from the Auth Sheet via Google Sheets API v4 + API key.

The Auth Sheet is NOT shared with the service account — it uses a plain API key.
"""
import os
from typing import Any

import httpx


def get_credentials() -> dict[str, str]:
    """Return {'email': ..., 'password': ...} from row 2 of the Auth Sheet."""
    sheet_id = os.environ["GOOGLE_AUTH_SHEET_ID"]
    api_key = os.environ["GOOGLE_SHEETS_API_KEY"]
    url = (
        f"https://sheets.googleapis.com/v4/spreadsheets/{sheet_id}"
        f"/values/Sheet1!A1:B2?key={api_key}"
    )
    response = httpx.get(url, timeout=10)
    response.raise_for_status()
    data: dict[str, Any] = response.json()
    rows: list[list[str]] = data.get("values", [])
    if len(rows) < 2:
        raise ValueError("Auth Sheet must have a header row and one credentials row")
    headers = rows[0]
    values = rows[1]
    return dict(zip(headers, values))
