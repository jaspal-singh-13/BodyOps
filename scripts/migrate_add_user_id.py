"""Migration: add user_id as first column to all existing Main Data Sheet tabs.

Safe to run multiple times — skips any tab that already has user_id as column A.
Fills all existing data rows with user_id = 1.
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

OK = "[OK]"
SKIP = "[SKIP]"
FAIL = "[FAIL]"
DONE = "[DONE]"


def get_client() -> gspread.Client:
    creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def migrate_tab(ws: gspread.Worksheet) -> str:
    """Insert user_id as column A if not already present. Returns status string."""
    all_values = ws.get_all_values()

    if not all_values:
        # Empty sheet — just write the header
        ws.update("A1", [["user_id"]])
        return f"{DONE} {ws.title} — was empty, added user_id header"

    headers = all_values[0]
    if headers and headers[0] == "user_id":
        return f"{SKIP} {ws.title} — user_id already in column A"

    num_rows = len(all_values)
    # Build the new column: header + "1" for every existing data row
    new_column = ["user_id"] + ["1"] * (num_rows - 1)
    ws.insert_cols([new_column], col=1)
    return f"{DONE} {ws.title} — inserted user_id column ({num_rows - 1} data rows set to 1)"


def main() -> None:
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
