"""
Bootstrap all Google Sheet tabs. Safe to run multiple times — idempotent.

What it does:
    1. Validates all required env vars; exits with code 1 if any are missing.
    2. Authenticates with the service account from ``GOOGLE_SERVICE_ACCOUNT_JSON``.
    3. Opens the Main Data Sheet and creates any missing tabs with correct headers.
    4. Opens the Chat History Sheet and creates the ``ChatHistory`` tab if missing.
    5. Prints a checklist: ``[OK] <tab> (exists)`` or ``[OK] <tab> (created)``.

Auth Sheet is NOT touched — the owner manages it manually in Google Sheets.

Schema reflects all applied migrations:
    - migrate_add_user_id.py     — user_id as first column on all tabs
    - migrate_add_weight_time.py — time column added to WeightLogs after date

Usage:
    python scripts/setup.py
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
    "GOOGLE_SHEETS_API_KEY",
    "GOOGLE_DRIVE_FOLDER_ID",
    "AZURE_OPENAI_API_KEY",
    "AZURE_OPENAI_ENDPOINT",
    "JWT_SECRET",
]

# Tab name → ordered list of header columns
MAIN_SHEET_TABS: dict[str, list[str]] = {
    "WeightLogs": ["user_id", "date", "time", "weight_kg", "logged_at"],
    "Meals": ["user_id", "id", "date", "meal_type", "photo_url", "total_calories", "total_protein_g", "total_carbs_g", "total_fat_g", "logged_at"],
    "MealItems": ["user_id", "id", "meal_id", "name", "quantity", "unit", "calories", "protein_g", "carbs_g", "fat_g"],
    "WorkoutPlans": ["user_id", "plan_id", "plan_name", "is_active", "created_at"],
    "WorkoutPrograms": ["user_id", "plan_id", "program_name", "day_name", "exercise_name", "sets", "rep_min", "rep_max", "order", "created_at"],
    "WorkoutSchedules": ["user_id", "plan_id", "weekday", "day_name", "created_at"],
    "WorkoutSessions": ["user_id", "plan_id", "session_id", "date", "day_name", "started_at", "completed_at"],
    "WorkoutSets": ["user_id", "session_id", "exercise_name", "set_number", "weight_kg", "reps", "logged_at"],
    "Tasks": ["user_id", "id", "name", "description", "task_type"],
    "DailyTaskStatus": ["user_id", "id", "task_id", "date", "completed", "completed_at"],
    "CoachInsights": ["user_id", "id", "date", "type", "summary", "wins_json", "focus_json", "next_step", "generated_at"],
    "Settings": ["user_id", "name", "current_weight_kg", "height_cm", "age", "goal_weight_kg", "start_date", "calorie_target", "protein_target_g", "wake_up_time", "unit_preference", "reminders_json", "updated_at"],
}

CHAT_HISTORY_TABS: dict[str, list[str]] = {
    "ChatHistory": ["user_id", "session_id", "date", "role", "content", "tool_calls_json"],
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

# Status prefix strings used in console output
OK = "[OK]"
FAIL = "[FAIL]"


def validate_env() -> None:
    """
    Check all required env vars are present; exit with code 1 if any are missing.

    Prints a list of missing variables and exits so the user knows exactly
    what to set before re-running.
    """
    missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        print(f"{FAIL} Missing required environment variables:")
        for v in missing:
            print(f"  - {v}")
        sys.exit(1)
    print(f"{OK} All required environment variables present")


def get_client() -> gspread.Client:
    """
    Build and return an authenticated gspread client.

    Reads ``GOOGLE_SERVICE_ACCOUNT_JSON`` from the environment and parses it.

    Returns:
        Authorised ``gspread.Client``.

    Raises:
        Exception: If authentication fails (prints error and caller exits).
    """
    creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def ensure_tabs(spreadsheet: gspread.Spreadsheet, tabs: dict[str, list[str]]) -> None:
    """
    Create missing tabs in a spreadsheet and write their header rows.

    For existing tabs, the current header row is compared against the expected
    schema. A mismatch is printed as a warning so the operator knows to run
    migrate_sheet_headers.py. Headers are never silently overwritten here to
    avoid accidental data loss.

    Each new worksheet is created with 1000 rows and the appropriate number
    of columns.

    Args:
        spreadsheet: Opened ``gspread.Spreadsheet`` to modify.
        tabs: Dict mapping tab name to ordered list of column header strings.
    """
    existing = {ws.title: ws for ws in spreadsheet.worksheets()}
    for tab_name, headers in tabs.items():
        if tab_name in existing:
            current_headers = existing[tab_name].row_values(1)
            if current_headers == headers:
                print(f"  {OK} {tab_name} (exists, headers correct)")
            else:
                print(f"  {FAIL} {tab_name} (exists but headers are WRONG)")
                print(f"        expected: {headers}")
                print(f"        actual:   {current_headers}")
                print(f"        → run: python scripts/migrate_sheet_headers.py")
        else:
            ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=len(headers))
            ws.append_row(headers)
            print(f"  {OK} {tab_name} (created)")


def main() -> None:
    """
    Entry point: validate env, connect to Sheets, and bootstrap all tabs.

    Exits with code 1 on any unrecoverable error (missing env vars or failed
    Sheets connection).
    """
    print("=== BodyOps Sheet Bootstrap ===\n")

    validate_env()

    print("\nConnecting to Google Sheets...")
    try:
        client = get_client()
        print(f"{OK} Service account authenticated\n")
    except Exception as e:
        print(f"{FAIL} Authentication failed: {e}")
        sys.exit(1)

    print("Main Data Sheet tabs:")
    try:
        main_sheet = client.open_by_key(os.environ["GOOGLE_SPREADSHEET_ID"])
        ensure_tabs(main_sheet, MAIN_SHEET_TABS)
    except Exception as e:
        print(f"{FAIL} Main Data Sheet error: {e}")
        sys.exit(1)

    print("\nChat History Sheet tabs:")
    try:
        chat_sheet = client.open_by_key(os.environ["GOOGLE_CHAT_HISTORY_SHEET_ID"])
        ensure_tabs(chat_sheet, CHAT_HISTORY_TABS)
    except Exception as e:
        print(f"{FAIL} Chat History Sheet error: {e}")
        sys.exit(1)

    print(f"\n{OK} Bootstrap complete - all tabs ready")


if __name__ == "__main__":
    main()
