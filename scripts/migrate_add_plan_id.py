"""
One-time migration: add plan_id support to workout tabs.

What this script does:
  1. Adds the ``WorkoutPlans`` tab (if missing) with headers:
         user_id | plan_id | plan_name | is_active | created_at
  2. For WorkoutPrograms, WorkoutSchedules, WorkoutSessions:
       - Reads all current data rows
       - Rewrites the header row to insert ``plan_id`` as the 2nd column
       - Stamps each existing row with a generated plan_id scoped per user
         (format: ``{user_id}-{unix_ms_at_migration_time}``)
  3. Creates one active ``WorkoutPlans`` row per user, using the
     ``program_name`` value from their first WorkoutPrograms row as the
     plan name (falls back to "Imported Plan" if absent).

After running this script:
  - Restart the API server (clears in-memory _header_cache).
  - No re-import required — existing data is preserved with plan_ids.

Usage:
    python scripts/migrate_add_plan_id.py
"""

import json
import os
import sys
import time
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

# New header schemas (matching setup.py)
NEW_HEADERS: dict[str, list[str]] = {
    "WorkoutPrograms": ["user_id", "plan_id", "program_name", "day_name", "exercise_name", "sets", "rep_min", "rep_max", "order", "created_at"],
    "WorkoutSchedules": ["user_id", "plan_id", "weekday", "day_name", "created_at"],
    "WorkoutSessions": ["user_id", "plan_id", "session_id", "date", "day_name", "started_at", "completed_at"],
}

PLANS_HEADERS = ["user_id", "plan_id", "plan_name", "is_active", "created_at"]

OK = "[OK]"
SKIP = "[SKIP]"
FIXED = "[FIXED]"
FAIL = "[FAIL]"


def get_client() -> gspread.Client:
    missing = [v for v in REQUIRED_VARS if not os.environ.get(v)]
    if missing:
        print(f"{FAIL} Missing env vars: {missing}")
        sys.exit(1)
    creds_dict = json.loads(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    creds = Credentials.from_service_account_info(creds_dict, scopes=SCOPES)
    return gspread.authorize(creds)


def _collect_users(tabs: dict[str, gspread.Worksheet]) -> dict[int, str]:
    """
    Return {user_id: plan_id} for every distinct user_id found in WorkoutPrograms.

    The plan_id is ``{user_id}-{current_unix_ms}`` — unique per user, stable
    within this migration run.
    """
    now_ms = int(time.time() * 1000)
    user_ids: set[int] = set()
    if "WorkoutPrograms" in tabs:
        for row in tabs["WorkoutPrograms"].get_all_records():
            try:
                user_ids.add(int(row.get("user_id", -1)))
            except (ValueError, TypeError):
                pass
    user_ids.discard(-1)
    return {uid: f"{uid}-{now_ms}" for uid in sorted(user_ids)}


def _program_name_for_user(programs_ws: gspread.Worksheet, user_id: int) -> str:
    """Return the program_name from the first WorkoutPrograms row for the user."""
    for row in programs_ws.get_all_records():
        if int(row.get("user_id", -1)) == user_id:
            name = str(row.get("program_name", "")).strip()
            if name:
                return name
    return "Imported Plan"


def migrate_tab(
    ws: gspread.Worksheet,
    tab_name: str,
    new_headers: list[str],
    user_plan_ids: dict[int, str],
) -> None:
    current_headers = ws.row_values(1)

    if current_headers == new_headers:
        print(f"  {OK} {tab_name} — headers already correct, no action needed")
        return

    if "plan_id" in current_headers:
        print(f"  {SKIP} {tab_name} — plan_id column already present")
        return

    all_rows = ws.get_all_records()
    print(f"  {FIXED} {tab_name} — adding plan_id column ({len(all_rows)} data rows)")

    # Build new rows with plan_id inserted as second column
    new_data_rows: list[list] = []
    for row in all_rows:
        try:
            uid = int(row.get("user_id", -1))
        except (ValueError, TypeError):
            uid = -1
        plan_id = user_plan_ids.get(uid, "")
        new_row = [row.get(h, "") for h in new_headers]
        # Inject plan_id at index 1
        new_row[1] = plan_id
        new_data_rows.append(new_row)

    ws.clear()
    ws.append_row(new_headers, value_input_option="USER_ENTERED")
    if new_data_rows:
        ws.append_rows(new_data_rows, value_input_option="RAW")
    print(f"         rewrote {len(new_data_rows)} rows with plan_id stamps")


def ensure_plans_tab(
    spreadsheet: gspread.Spreadsheet,
    existing_tabs: dict[str, gspread.Worksheet],
    user_plan_ids: dict[int, str],
    programs_ws: gspread.Worksheet | None,
) -> None:
    now_iso = __import__("datetime").datetime.utcnow().isoformat() + "Z"

    if "WorkoutPlans" in existing_tabs:
        ws = existing_tabs["WorkoutPlans"]
        current_headers = ws.row_values(1)
        if current_headers == PLANS_HEADERS:
            existing_records = ws.get_all_records()
            existing_user_ids = {int(r.get("user_id", -1)) for r in existing_records}
            newly_added = 0
            for uid, plan_id in user_plan_ids.items():
                if uid not in existing_user_ids:
                    pname = _program_name_for_user(programs_ws, uid) if programs_ws else "Imported Plan"
                    ws.append_row([uid, plan_id, pname, "TRUE", now_iso], value_input_option="RAW")
                    newly_added += 1
            if newly_added:
                print(f"  {FIXED} WorkoutPlans — added {newly_added} new user row(s)")
            else:
                print(f"  {OK} WorkoutPlans — already present and complete")
            return
        else:
            print(f"  {FAIL} WorkoutPlans exists but headers wrong: {current_headers}")
            print(f"         expected: {PLANS_HEADERS}")
            print(f"         → fix manually or drop the tab and re-run")
            return

    ws = spreadsheet.add_worksheet(title="WorkoutPlans", rows=200, cols=len(PLANS_HEADERS))
    ws.append_row(PLANS_HEADERS, value_input_option="USER_ENTERED")
    rows_added = 0
    for uid, plan_id in user_plan_ids.items():
        pname = _program_name_for_user(programs_ws, uid) if programs_ws else "Imported Plan"
        ws.append_row([uid, plan_id, pname, "TRUE", now_iso], value_input_option="RAW")
        rows_added += 1
    print(f"  {OK} WorkoutPlans — created with {rows_added} user row(s)")


def main() -> None:
    print("=== BodyOps plan_id Migration ===\n")

    client = get_client()
    spreadsheet = client.open_by_key(os.environ["GOOGLE_SPREADSHEET_ID"])
    existing_tabs = {ws.title: ws for ws in spreadsheet.worksheets()}

    # Collect users and generate plan_ids before touching any tab
    programs_ws = existing_tabs.get("WorkoutPrograms")
    user_plan_ids = _collect_users(existing_tabs)
    print(f"Found {len(user_plan_ids)} user(s) with workout data: {list(user_plan_ids.keys())}\n")

    print("Migrating workout tabs:")
    for tab_name, new_headers in NEW_HEADERS.items():
        if tab_name not in existing_tabs:
            print(f"  {SKIP} {tab_name} — tab does not exist (run setup.py first)")
            continue
        try:
            migrate_tab(existing_tabs[tab_name], tab_name, new_headers, user_plan_ids)
        except Exception as e:
            print(f"  {FAIL} {tab_name} — {e}")

    print("\nEnsuring WorkoutPlans tab:")
    try:
        ensure_plans_tab(spreadsheet, existing_tabs, user_plan_ids, programs_ws)
    except Exception as e:
        print(f"  {FAIL} WorkoutPlans — {e}")

    print(f"\n=== Done ===")
    print("Next steps:")
    print("  1. Restart the API server to clear the in-memory header cache.")
    print("  2. No re-import required — existing data has been stamped with plan_ids.")


if __name__ == "__main__":
    main()
