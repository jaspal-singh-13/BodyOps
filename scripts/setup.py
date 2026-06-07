"""Bootstrap all Google Sheet tabs. Safe to run multiple times - idempotent."""
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

MAIN_SHEET_TABS: dict[str, list[str]] = {
    "WeightLogs": ["id", "date", "weight_kg", "logged_at"],
    "Meals": ["id", "date", "meal_type", "photo_url", "total_calories", "total_protein_g", "total_carbs_g", "total_fat_g", "logged_at"],
    "MealItems": ["id", "meal_id", "name", "quantity", "unit", "calories", "protein_g", "carbs_g", "fat_g"],
    "WorkoutPrograms": ["id", "name", "created_at"],
    "WorkoutSchedules": ["id", "program_id", "weekday", "workout_day_name"],
    "WorkoutSessions": ["id", "date", "workout_day_name", "started_at", "completed_at"],
    "WorkoutSets": ["id", "session_id", "exercise_name", "set_number", "weight_kg", "reps", "logged_at"],
    "Tasks": ["id", "name", "description", "task_type"],
    "DailyTaskStatus": ["id", "task_id", "date", "completed", "completed_at"],
    "CoachInsights": ["id", "date", "type", "summary", "wins_json", "focus_json", "next_step", "generated_at"],
    "Settings": ["name", "current_weight_kg", "height_cm", "age", "goal_weight_kg", "start_date", "calorie_target", "protein_target_g", "wake_up_time", "unit_preference", "reminders_json", "updated_at"],
}

CHAT_HISTORY_TABS: dict[str, list[str]] = {
    "ChatHistory": ["session_id", "date", "role", "content", "tool_calls_json"],
}

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

OK = "[OK]"
FAIL = "[FAIL]"


def validate_env() -> None:
    missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        print(f"{FAIL} Missing required environment variables:")
        for v in missing:
            print(f"  - {v}")
        sys.exit(1)
    print(f"{OK} All required environment variables present")


def get_client() -> gspread.Client:
    creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def ensure_tabs(spreadsheet: gspread.Spreadsheet, tabs: dict[str, list[str]]) -> None:
    existing = {ws.title for ws in spreadsheet.worksheets()}
    for tab_name, headers in tabs.items():
        if tab_name in existing:
            print(f"  {OK} {tab_name} (exists)")
        else:
            ws = spreadsheet.add_worksheet(title=tab_name, rows=1000, cols=len(headers))
            ws.append_row(headers)
            print(f"  {OK} {tab_name} (created)")


def main() -> None:
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
