"""
One-time migration: fix Google Sheet tabs whose header rows don't match the
schema defined in setup.py.

The WorkoutSchedules tab was originally created with the old PRD schema:
    user_id | id | program_id | weekday | workout_day_name

The live code expects:
    user_id | weekday | day_name | created_at

Because the column names don't match, every import silently stored day_name
values in the wrong column (empty string) and every schedule read returned
"Rest" for all days.

What this script does for each tab in MAIN_SHEET_TABS:
  1. Reads the current header row (row 1).
  2. If it matches the expected schema → prints OK, skips.
  3. If it doesn't match → clears ALL rows (header + data) and rewrites the
     correct header row.  Existing data rows are discarded because they were
     written with the wrong column mapping and are effectively corrupt.

After running this script:
  - Restart the API server (clears in-memory _header_cache).
  - Re-import your workout plan via the Import tab.

Usage:
    python scripts/migrate_sheet_headers.py
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

# Canonical expected headers per tab (copied from setup.py)
MAIN_SHEET_TABS: dict[str, list[str]] = {
    "WeightLogs": ["user_id", "date", "time", "weight_kg", "logged_at"],
    "Meals": ["user_id", "id", "date", "meal_type", "photo_url", "total_calories", "total_protein_g", "total_carbs_g", "total_fat_g", "logged_at"],
    "MealItems": ["user_id", "id", "meal_id", "name", "quantity", "unit", "calories", "protein_g", "carbs_g", "fat_g"],
    "WorkoutPrograms": ["user_id", "program_name", "day_name", "exercise_name", "sets", "rep_min", "rep_max", "order", "created_at"],
    "WorkoutSchedules": ["user_id", "weekday", "day_name", "created_at"],
    "WorkoutSessions": ["user_id", "session_id", "date", "day_name", "started_at", "completed_at"],
    "WorkoutSets": ["user_id", "session_id", "exercise_name", "set_number", "weight_kg", "reps", "logged_at"],
    "Tasks": ["user_id", "id", "name", "description", "task_type"],
    "DailyTaskStatus": ["user_id", "id", "task_id", "date", "completed", "completed_at"],
    "CoachInsights": ["user_id", "id", "date", "type", "summary", "wins_json", "focus_json", "next_step", "generated_at"],
    "Settings": ["user_id", "name", "current_weight_kg", "height_cm", "age", "goal_weight_kg", "start_date", "calorie_target", "protein_target_g", "wake_up_time", "unit_preference", "reminders_json", "updated_at"],
}

OK = "[OK]"
FIXED = "[FIXED]"
SKIP = "[SKIP]"
FAIL = "[FAIL]"


def get_client() -> gspread.Client:
    missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        print(f"{FAIL} Missing env vars: {missing}")
        sys.exit(1)
    creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def migrate_tab(ws: gspread.Worksheet, tab_name: str, expected_headers: list[str]) -> None:
    current_headers = ws.row_values(1)

    if current_headers == expected_headers:
        print(f"  {OK} {tab_name} — headers correct, no action needed")
        return

    print(f"  {FIXED} {tab_name}")
    print(f"         old headers: {current_headers}")
    print(f"         new headers: {expected_headers}")

    # Count data rows so the user knows what's being dropped
    all_rows = ws.get_all_values()
    data_row_count = max(0, len(all_rows) - 1)
    if data_row_count:
        print(f"         discarding {data_row_count} data row(s) with wrong column mapping")

    # Clear everything and rewrite the correct header row
    ws.clear()
    ws.append_row(expected_headers, value_input_option="USER_ENTERED")
    print(f"         header row rewritten — re-import data after restarting the server")


def main() -> None:
    print("=== BodyOps Sheet Header Migration ===\n")

    client = get_client()
    spreadsheet = client.open_by_key(os.environ["GOOGLE_SPREADSHEET_ID"])
    existing_tabs = {ws.title: ws for ws in spreadsheet.worksheets()}

    print("Checking Main Data Sheet tabs:")
    for tab_name, expected_headers in MAIN_SHEET_TABS.items():
        if tab_name not in existing_tabs:
            print(f"  {SKIP} {tab_name} — tab does not exist (run setup.py first)")
            continue
        try:
            migrate_tab(existing_tabs[tab_name], tab_name, expected_headers)
        except Exception as e:
            print(f"  {FAIL} {tab_name} — {e}")

    print(f"\n=== Done ===")
    print("Next steps:")
    print("  1. Restart the API server to clear the in-memory header cache.")
    print("  2. Re-import your workout plan via the Import tab.")


if __name__ == "__main__":
    main()
