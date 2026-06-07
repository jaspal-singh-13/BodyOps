"""Read credentials from the Auth Sheet via service account."""
import os

from .sheets_client import get_client


def get_credentials() -> dict:
    """Return {'user_id': int, 'email': str, 'password': str} from row 2 of the Auth Sheet."""
    sheet_id = os.environ["GOOGLE_AUTH_SHEET_ID"]
    spreadsheet = get_client().open_by_key(sheet_id)
    ws = spreadsheet.sheet1
    rows = ws.get_all_records()
    if not rows:
        raise ValueError("Auth Sheet has no data rows")
    row = rows[0]
    if "email" not in row or "password" not in row:
        raise ValueError("Auth Sheet must have 'email' and 'password' columns")
    return {
        "user_id": int(row["user_id"]) if row.get("user_id") else 1,
        "email": str(row["email"]),
        "password": str(row["password"]),
    }
