"""
Migration: add ``time`` column to the WeightLogs tab after ``date``.

Safe to run multiple times — skips if ``time`` already exists in the header.
Existing rows are filled with an empty string so they sort before any timed
entry and the backend's ``r.get("time", "")`` fallback stays consistent.

Expected column order after migration:
    user_id | date | time | weight_kg | logged_at

Usage:
    python scripts/migrate_add_weight_time.py
"""

import json
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / "api" / ".env")

import gspread
from google.oauth2.service_account import Credentials

REQUIRED_VARS = [
    "GOOGLE_SERVICE_ACCOUNT_JSON",
    "GOOGLE_SPREADSHEET_ID",
]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

OK   = "[OK]"
SKIP = "[SKIP]"
FAIL = "[FAIL]"
DONE = "[DONE]"


def get_client() -> gspread.Client:
    creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def migrate(ws: gspread.Worksheet) -> str:
    all_values = ws.get_all_values()

    if not all_values:
        return f"{SKIP} WeightLogs — sheet is empty, nothing to migrate"

    headers = all_values[0]

    if "time" in headers:
        return f"{SKIP} WeightLogs — 'time' column already exists"

    if "date" not in headers:
        return f"{FAIL} WeightLogs — expected 'date' column not found (headers: {headers})"

    # Insert the new column immediately after 'date' (columns are 1-based)
    date_col = headers.index("date") + 1  # 1-based position of 'date'
    insert_at = date_col + 1              # insert after date

    num_rows = len(all_values)
    # Header + empty string for every existing data row
    new_column = ["time"] + [""] * (num_rows - 1)
    ws.insert_cols([new_column], col=insert_at)

    return f"{DONE} WeightLogs — inserted 'time' column at position {insert_at} ({num_rows - 1} existing rows set to empty)"


def main() -> None:
    print("=== BodyOps Migration: add 'time' column to WeightLogs ===\n")

    missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        print(f"{FAIL} Missing required environment variables: {', '.join(missing)}")
        sys.exit(1)

    try:
        client = get_client()
        sheet = client.open_by_key(os.environ["GOOGLE_SPREADSHEET_ID"])
        print(f"{OK} Connected to Main Data Sheet\n")
    except Exception as e:
        print(f"{FAIL} Could not connect: {e}")
        sys.exit(1)

    existing_tabs = {ws.title: ws for ws in sheet.worksheets()}

    if "WeightLogs" not in existing_tabs:
        print(f"{SKIP} WeightLogs — tab does not exist (run setup.py first)")
        sys.exit(0)

    result = migrate(existing_tabs["WeightLogs"])
    print(f"  {result}")

    print("\n=== Migration complete ===")
    print("Restart the backend to clear the header cache.")


if __name__ == "__main__":
    main()
