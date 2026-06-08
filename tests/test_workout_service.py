"""
Unit tests for workout_service functions introduced/changed in the schedule tab work.

Covers:
  - get_schedule: 7-day structure, exercise mapping, gap filling, empty state
  - get_today_workout: session_id, is_completed, sets_logged_today in response
  - import_workout: schedule gap fill ensures all 7 weekdays are written
"""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-sheet-id")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")

from unittest.mock import patch, call

import pytest

from api.services.workout_service import get_schedule, get_today_workout, import_workout
from api.models.workout import ExerciseInfo, WorkoutDaySummary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _schedule_row(user_id: int, weekday: int, day_name: str) -> dict:
    return {"user_id": user_id, "weekday": weekday, "day_name": day_name, "created_at": ""}


def _program_row(user_id: int, program_name: str, day_name: str, exercise_name: str,
                 sets: int = 3, rep_min: int = 8, rep_max: int = 12, order: int = 1) -> dict:
    return {
        "user_id": user_id,
        "program_name": program_name,
        "day_name": day_name,
        "exercise_name": exercise_name,
        "sets": sets,
        "rep_min": rep_min,
        "rep_max": rep_max,
        "order": order,
        "created_at": "",
    }


def _session_row(user_id: int, session_id: str, date: str, completed_at: str = "") -> dict:
    return {
        "user_id": user_id,
        "session_id": session_id,
        "date": date,
        "day_name": "Push",
        "started_at": "2026-06-08T10:00:00+00:00",
        "completed_at": completed_at,
    }


def _set_row(user_id: int, session_id: str, exercise_name: str, set_number: int = 1) -> dict:
    return {
        "user_id": user_id,
        "session_id": session_id,
        "exercise_name": exercise_name,
        "set_number": set_number,
        "weight_kg": 60.0,
        "reps": 10,
        "logged_at": "2026-06-08T10:05:00+00:00",
    }


# ---------------------------------------------------------------------------
# get_schedule — structure and mapping
# ---------------------------------------------------------------------------


class TestGetSchedule:
    def test_always_returns_7_days(self):
        schedule_rows = [
            _schedule_row(1, 0, "Push"),
            _schedule_row(1, 2, "Pull"),
        ]
        with patch("api.services.workout_service._safe_read_rows", side_effect=[schedule_rows, []]):
            result = get_schedule(user_id=1)
        assert len(result.days) == 7

    def test_weekdays_are_in_order_mon_to_sun(self):
        with patch("api.services.workout_service._safe_read_rows", side_effect=[[], []]):
            result = get_schedule(user_id=1)
        assert [d.weekday for d in result.days] == list(range(7))
        assert result.days[0].weekday_name == "Monday"
        assert result.days[6].weekday_name == "Sunday"

    def test_missing_weekdays_default_to_rest(self):
        # Only Mon (0) and Wed (2) have schedule entries — Tue, Thu-Sun should be Rest
        schedule_rows = [
            _schedule_row(1, 0, "Push"),
            _schedule_row(1, 2, "Pull"),
        ]
        with patch("api.services.workout_service._safe_read_rows", side_effect=[schedule_rows, []]):
            result = get_schedule(user_id=1)
        rest_weekdays = {d.weekday for d in result.days if d.is_rest}
        assert rest_weekdays == {1, 3, 4, 5, 6}

    def test_exercises_mapped_to_correct_day(self):
        schedule_rows = [_schedule_row(1, 0, "Push")]
        program_rows = [
            _program_row(1, "PPL", "Push", "Bench Press", sets=3, rep_min=8, rep_max=12, order=1),
            _program_row(1, "PPL", "Push", "OHP", sets=3, rep_min=8, rep_max=10, order=2),
        ]
        with patch("api.services.workout_service._safe_read_rows", side_effect=[schedule_rows, program_rows]):
            result = get_schedule(user_id=1)
        monday = result.days[0]
        assert monday.day_name == "Push"
        assert monday.is_rest is False
        assert len(monday.exercises) == 2
        assert monday.exercises[0].exercise_name == "Bench Press"
        assert monday.exercises[1].exercise_name == "OHP"

    def test_rest_day_has_empty_exercises(self):
        schedule_rows = [_schedule_row(1, 5, "Rest")]
        with patch("api.services.workout_service._safe_read_rows", side_effect=[schedule_rows, []]):
            result = get_schedule(user_id=1)
        saturday = result.days[5]
        assert saturday.is_rest is True
        assert saturday.exercises == []

    def test_program_name_extracted_from_first_program_row(self):
        schedule_rows = [_schedule_row(1, 0, "Push")]
        program_rows = [_program_row(1, "PPL v2", "Push", "Bench Press")]
        with patch("api.services.workout_service._safe_read_rows", side_effect=[schedule_rows, program_rows]):
            result = get_schedule(user_id=1)
        assert result.program_name == "PPL v2"

    def test_no_schedule_no_program_returns_all_rest_and_no_program_name(self):
        with patch("api.services.workout_service._safe_read_rows", side_effect=[[], []]):
            result = get_schedule(user_id=1)
        assert result.program_name is None
        assert all(d.is_rest for d in result.days)

    def test_ignores_rows_from_other_users(self):
        schedule_rows = [
            _schedule_row(1, 0, "Push"),
            _schedule_row(2, 1, "Pull"),  # different user
        ]
        program_rows = [
            _program_row(2, "Other", "Pull", "Row"),  # different user
        ]
        with patch("api.services.workout_service._safe_read_rows", side_effect=[schedule_rows, program_rows]):
            result = get_schedule(user_id=1)
        assert result.program_name is None
        assert result.days[0].day_name == "Push"
        assert result.days[1].day_name == "Rest"  # Pull row from user 2 not used


# ---------------------------------------------------------------------------
# get_today_workout — session state fields
# ---------------------------------------------------------------------------


class TestGetTodayWorkoutSessionState:
    def _make_patch(self, schedule_rows, program_rows, set_rows, session_rows):
        def side_effect(tab):
            from api.services.workout_service import SCHEDULES_TAB, PROGRAMS_TAB, SETS_TAB, SESSIONS_TAB
            return {
                SCHEDULES_TAB: schedule_rows,
                PROGRAMS_TAB: program_rows,
                SETS_TAB: set_rows,
                SESSIONS_TAB: session_rows,
            }[tab]
        return side_effect

    # Use 2026-06-08 (Monday, weekday=0) throughout so schedule_row(weekday=0) matches.
    _MONDAY = "2026-06-08"
    _SESSION_ID = "1-2026-06-08"

    def test_session_id_is_none_when_no_session_exists(self):
        schedule_rows = [_schedule_row(1, 0, "Push")]
        program_rows = [_program_row(1, "PPL", "Push", "Bench Press")]
        side_effect = self._make_patch(schedule_rows, program_rows, [], [])
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.session_id is None
        assert result.is_completed is False

    def test_session_id_returned_when_session_exists(self):
        schedule_rows = [_schedule_row(1, 0, "Push")]
        program_rows = [_program_row(1, "PPL", "Push", "Bench Press")]
        session_rows = [_session_row(1, self._SESSION_ID, self._MONDAY)]
        side_effect = self._make_patch(schedule_rows, program_rows, [], session_rows)
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.session_id == self._SESSION_ID
        assert result.is_completed is False

    def test_is_completed_true_when_completed_at_set(self):
        schedule_rows = [_schedule_row(1, 0, "Push")]
        program_rows = [_program_row(1, "PPL", "Push", "Bench Press")]
        session_rows = [_session_row(1, self._SESSION_ID, self._MONDAY, completed_at="2026-06-08T11:00:00+00:00")]
        side_effect = self._make_patch(schedule_rows, program_rows, [], session_rows)
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.is_completed is True

    def test_sets_logged_today_counts_only_todays_sets(self):
        schedule_rows = [_schedule_row(1, 0, "Push")]
        program_rows = [_program_row(1, "PPL", "Push", "Bench Press")]
        set_rows = [
            _set_row(1, self._SESSION_ID, "Bench Press", set_number=1),
            _set_row(1, self._SESSION_ID, "Bench Press", set_number=2),
            _set_row(1, "1-2026-06-07", "Bench Press", set_number=1),  # previous session
        ]
        session_rows = [_session_row(1, self._SESSION_ID, self._MONDAY)]
        side_effect = self._make_patch(schedule_rows, program_rows, set_rows, session_rows)
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        bench = next(e for e in result.exercises if e.exercise_name == "Bench Press")
        assert bench.sets_logged_today == 2

    def test_sets_logged_today_zero_for_exercise_not_yet_started(self):
        schedule_rows = [_schedule_row(1, 0, "Push")]
        program_rows = [
            _program_row(1, "PPL", "Push", "Bench Press", order=1),
            _program_row(1, "PPL", "Push", "OHP", order=2),
        ]
        set_rows = [_set_row(1, self._SESSION_ID, "Bench Press", set_number=1)]
        session_rows = [_session_row(1, self._SESSION_ID, self._MONDAY)]
        side_effect = self._make_patch(schedule_rows, program_rows, set_rows, session_rows)
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        ohp = next(e for e in result.exercises if e.exercise_name == "OHP")
        assert ohp.sets_logged_today == 0

    def test_rest_day_returns_no_session_state(self):
        schedule_rows = [_schedule_row(1, 0, "Rest")]
        side_effect = self._make_patch(schedule_rows, [], [], [])
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.is_rest_day is True
        assert result.session_id is None
        assert result.is_completed is False


# ---------------------------------------------------------------------------
# import_workout — schedule gap fill
# ---------------------------------------------------------------------------


class TestImportWorkoutScheduleGapFill:
    def _run_import(self, schedule: list[tuple[int, str]]):
        days = [WorkoutDaySummary(day_name="Push", exercises=[
            ExerciseInfo(exercise_name="Bench Press", sets=3, rep_min=8, rep_max=12, order=1),
        ])]
        written_rows: list[dict] = []

        def fake_delete(tab, user_id):
            pass

        def fake_append_batch(tab, rows):
            from api.services.workout_service import SCHEDULES_TAB
            if tab == SCHEDULES_TAB:
                written_rows.extend(rows)

        def fake_append(tab, row):
            pass

        with (
            patch("api.services.workout_service._delete_user_rows", side_effect=fake_delete),
            patch("api.services.workout_service.append_rows_batch", side_effect=fake_append_batch),
            patch("api.services.workout_service.append_row", side_effect=fake_append),
        ):
            import_workout(user_id=1, program_name="PPL", days=days, schedule=schedule)

        return written_rows

    def test_all_7_weekdays_written_when_schedule_is_complete(self):
        full_schedule = [(i, "Push" if i < 5 else "Rest") for i in range(7)]
        rows = self._run_import(full_schedule)
        weekdays = {r["weekday"] for r in rows}
        assert weekdays == set(range(7))

    def test_missing_weekdays_filled_with_rest(self):
        # Only provide Mon (0) and Wed (2)
        partial_schedule = [(0, "Push"), (2, "Pull")]
        rows = self._run_import(partial_schedule)
        weekdays = {r["weekday"] for r in rows}
        assert weekdays == set(range(7))
        rest_weekdays = {r["weekday"] for r in rows if r["day_name"] == "Rest"}
        assert rest_weekdays == {1, 3, 4, 5, 6}

    def test_empty_schedule_fills_all_7_as_rest(self):
        rows = self._run_import([])
        assert len(rows) == 7
        assert all(r["day_name"] == "Rest" for r in rows)

    def test_explicit_rest_entries_preserved(self):
        schedule = [(0, "Push"), (1, "Rest"), (2, "Pull")]
        rows = self._run_import(schedule)
        tuesday = next(r for r in rows if r["weekday"] == 1)
        assert tuesday["day_name"] == "Rest"

    def test_no_duplicate_weekdays(self):
        schedule = [(0, "Push"), (1, "Pull"), (2, "Legs"), (3, "Rest"), (4, "Push")]
        rows = self._run_import(schedule)
        weekdays = [r["weekday"] for r in rows]
        assert len(weekdays) == len(set(weekdays)), "duplicate weekdays written"
