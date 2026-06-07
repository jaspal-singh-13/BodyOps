"""
Migration: add user_id as the first column to all Main Data Sheet tabs.

Safe to run multiple times — skips any tab that already has ``user_id``
as column A. Fills all existing data rows with ``user_id = 1``.

This migration is needed once when upgrading from the initial single-user
schema (no user_id column) to the scoped multi-user-ready schema.

Usage:
    python scripts/migrate_add_user_id.py

After running:
    Update the Auth Sheet manually — add ``user_id`` as the first column
    with value ``1`` for the existing credential row.
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
    "GOOGLE_CHAT_HISTORY_SHEET_ID",
]

# All tabs in the Main Data Sheet that should receive the user_id column
MAIN_SHEET_TABS = [
    "WeightLogs",
    "Meals",
    "MealItems",
    "WorkoutPrograms",
    "WorkoutSchedules",
    "WorkoutSessions",
    "WorkoutSets",
    "Tasks",
    "DailyTaskStatus",
    "CoachInsights",
    "Settings",
]

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Status prefix strings used in console output
OK = "[OK]"
SKIP = "[SKIP]"
FAIL = "[FAIL]"
DONE = "[DONE]"


def get_client() -> gspread.Client:
    """
    Build and return an authenticated gspread client.

    Returns:
        Authorised ``gspread.Client``.
    """
    creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def migrate_tab(ws: gspread.Worksheet) -> str:
    """
    Insert ``user_id`` as column A if not already present.

    If the sheet is empty, writes only the ``user_id`` header cell.
    If the sheet already has ``user_id`` in column A, skips it.
    Otherwise inserts a new column A and fills all data rows with ``"1"``.

    Args:
        ws: The worksheet to migrate.

    Returns:
        A human-readable status string starting with one of:
        ``[DONE]``, ``[SKIP]``, indicating what happened.
    """
    all_values = ws.get_all_values()

    if not all_values:
        # Empty sheet — write the header so it's ready for data
        ws.update("A1", [["user_id"]])
        return f"{DONE} {ws.title} — was empty, added user_id header"

    headers = all_values[0]
    if headers and headers[0] == "user_id":
        return f"{SKIP} {ws.title} — user_id already in column A"

    num_rows = len(all_values)
    # New column: header + value "1" for every existing data row
    new_column = ["user_id"] + ["1"] * (num_rows - 1)
    ws.insert_cols([new_column], col=1)
    return f"{DONE} {ws.title} — inserted user_id column ({num_rows - 1} data rows set to 1)"


def main() -> None:
    """
    Entry point: connect to Sheets and migrate all applicable tabs.

    Tabs that already have user_id are silently skipped. Tabs that don't
    exist yet (not created by setup.py) are also skipped with a message.
    """
    print("=== BodyOps Migration: add user_id to all tabs ===\n")

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

    print("Main Data Sheet:")
    for tab_name in MAIN_SHEET_TABS:
        if tab_name not in existing_tabs:
            print(f"  {SKIP} {tab_name} — does not exist (run setup.py to create it)")
            continue
        try:
            result = migrate_tab(existing_tabs[tab_name])
            print(f"  {result}")
        except Exception as e:
            print(f"  {FAIL} {tab_name} — {e}")

    print("\nChat History Sheet:")
    try:
        chat_sheet = client.open_by_key(os.environ["GOOGLE_CHAT_HISTORY_SHEET_ID"])
        chat_tabs = {ws.title: ws for ws in chat_sheet.worksheets()}
        if "ChatHistory" not in chat_tabs:
            print(f"  {SKIP} ChatHistory — does not exist (run setup.py to create it)")
        else:
            result = migrate_tab(chat_tabs["ChatHistory"])
            print(f"  {result}")
    except Exception as e:
        print(f"  {FAIL} Chat History Sheet — {e}")

    print(f"\n=== Migration complete ===")
    print("Reminder: update your Auth Sheet manually — add 'user_id' as the first column with value 1.")


if __name__ == "__main__":
    main()
