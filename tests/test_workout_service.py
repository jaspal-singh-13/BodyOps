"""
Unit tests for workout_service functions.

Covers:
  - get_schedule: 7-day structure, exercise mapping, gap filling, empty state
  - get_today_workout: session_id, is_completed, sets_logged_today in response
  - import_workout: non-destructive — appends new plan, does not delete old data
  - Plan management: get_active_plan_id, list_plans, activate_plan, delete_plan
  - Legacy fallback: functions work when no WorkoutPlans rows exist
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

from unittest.mock import MagicMock, patch, call

import pytest

from api.services.workout_service import (
    activate_plan,
    delete_plan,
    get_active_plan_id,
    get_schedule,
    get_today_workout,
    import_workout,
    list_plans,
)
from api.models.workout import ExerciseInfo, WorkoutDaySummary


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _plan_row(user_id: int, plan_id: str, plan_name: str, is_active: bool = False) -> dict:
    return {
        "user_id": user_id,
        "plan_id": plan_id,
        "plan_name": plan_name,
        "is_active": "TRUE" if is_active else "FALSE",
        "created_at": "2026-01-01T00:00:00Z",
    }


def _schedule_row(user_id: int, weekday: int, day_name: str, plan_id: str = "") -> dict:
    return {"user_id": user_id, "plan_id": plan_id, "weekday": weekday, "day_name": day_name, "created_at": ""}


def _program_row(user_id: int, program_name: str, day_name: str, exercise_name: str,
                 sets: int = 3, rep_min: int = 8, rep_max: int = 12, order: int = 1,
                 plan_id: str = "") -> dict:
    return {
        "user_id": user_id,
        "plan_id": plan_id,
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
        "plan_id": "",
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
# get_active_plan_id
# ---------------------------------------------------------------------------


class TestGetActivePlanId:
    def test_returns_active_plan_id(self):
        plan_rows = [
            _plan_row(1, "1-111", "PPL", is_active=False),
            _plan_row(1, "1-222", "Cut", is_active=True),
        ]
        with patch("api.services.workout_service._safe_read_rows", return_value=plan_rows):
            result = get_active_plan_id(user_id=1)
        assert result == "1-222"

    def test_returns_none_when_no_plans_tab(self):
        with patch("api.services.workout_service._safe_read_rows", return_value=[]):
            result = get_active_plan_id(user_id=1)
        assert result is None

    def test_returns_none_when_no_active_row_for_user(self):
        plan_rows = [_plan_row(2, "2-111", "Other", is_active=True)]
        with patch("api.services.workout_service._safe_read_rows", return_value=plan_rows):
            result = get_active_plan_id(user_id=1)
        assert result is None


# ---------------------------------------------------------------------------
# get_schedule — structure and mapping
# ---------------------------------------------------------------------------


class TestGetSchedule:
    PLAN_ID = "1-abc"

    def _make_patch(self, plan_rows, schedule_rows, program_rows):
        def side_effect(tab):
            from api.services.workout_service import PLANS_TAB, SCHEDULES_TAB, PROGRAMS_TAB
            return {
                PLANS_TAB: plan_rows,
                SCHEDULES_TAB: schedule_rows,
                PROGRAMS_TAB: program_rows,
            }[tab]
        return side_effect

    def test_always_returns_7_days(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [
            _schedule_row(1, 0, "Push", self.PLAN_ID),
            _schedule_row(1, 2, "Pull", self.PLAN_ID),
        ]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_patch(plan_rows, schedule_rows, [])):
            result = get_schedule(user_id=1)
        assert len(result.days) == 7

    def test_weekdays_are_in_order_mon_to_sun(self):
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_patch([], [], [])):
            result = get_schedule(user_id=1)
        assert [d.weekday for d in result.days] == list(range(7))
        assert result.days[0].weekday_name == "Monday"
        assert result.days[6].weekday_name == "Sunday"

    def test_missing_weekdays_default_to_rest(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [
            _schedule_row(1, 0, "Push", self.PLAN_ID),
            _schedule_row(1, 2, "Pull", self.PLAN_ID),
        ]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_patch(plan_rows, schedule_rows, [])):
            result = get_schedule(user_id=1)
        rest_weekdays = {d.weekday for d in result.days if d.is_rest}
        assert rest_weekdays == {1, 3, 4, 5, 6}

    def test_exercises_mapped_to_correct_day(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        program_rows = [
            _program_row(1, "PPL", "Push", "Bench Press", sets=3, rep_min=8, rep_max=12, order=1, plan_id=self.PLAN_ID),
            _program_row(1, "PPL", "Push", "OHP", sets=3, rep_min=8, rep_max=10, order=2, plan_id=self.PLAN_ID),
        ]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_patch(plan_rows, schedule_rows, program_rows)):
            result = get_schedule(user_id=1)
        monday = result.days[0]
        assert monday.day_name == "Push"
        assert monday.is_rest is False
        assert len(monday.exercises) == 2
        assert monday.exercises[0].exercise_name == "Bench Press"
        assert monday.exercises[1].exercise_name == "OHP"

    def test_rest_day_has_empty_exercises(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 5, "Rest", self.PLAN_ID)]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_patch(plan_rows, schedule_rows, [])):
            result = get_schedule(user_id=1)
        saturday = result.days[5]
        assert saturday.is_rest is True
        assert saturday.exercises == []

    def test_program_name_from_plans_tab(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL v2", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        program_rows = [_program_row(1, "PPL v2", "Push", "Bench Press", plan_id=self.PLAN_ID)]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_patch(plan_rows, schedule_rows, program_rows)):
            result = get_schedule(user_id=1)
        assert result.program_name == "PPL v2"

    def test_no_schedule_no_program_returns_all_rest_and_no_program_name(self):
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_patch([], [], [])):
            result = get_schedule(user_id=1)
        assert result.program_name is None
        assert all(d.is_rest for d in result.days)

    def test_ignores_rows_from_other_plans(self):
        """Exercises from a different plan_id must not bleed into the active plan's schedule."""
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        program_rows = [
            _program_row(1, "PPL", "Push", "Bench Press", plan_id=self.PLAN_ID),
            _program_row(1, "Old", "Push", "Old Exercise", plan_id="1-old"),
        ]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_patch(plan_rows, schedule_rows, program_rows)):
            result = get_schedule(user_id=1)
        monday = result.days[0]
        assert len(monday.exercises) == 1
        assert monday.exercises[0].exercise_name == "Bench Press"

    def test_legacy_fallback_no_plans_tab(self):
        """With no WorkoutPlans rows (legacy), all user rows are returned."""
        schedule_rows = [_schedule_row(1, 0, "Push", "")]
        program_rows = [_program_row(1, "Old PPL", "Push", "Bench Press", plan_id="")]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_patch([], schedule_rows, program_rows)):
            result = get_schedule(user_id=1)
        assert result.days[0].day_name == "Push"
        assert len(result.days[0].exercises) == 1


# ---------------------------------------------------------------------------
# get_today_workout — session state fields
# ---------------------------------------------------------------------------


class TestGetTodayWorkoutSessionState:
    PLAN_ID = "1-abc"

    def _make_patch(self, plan_rows, schedule_rows, program_rows, set_rows, session_rows):
        def side_effect(tab):
            from api.services.workout_service import PLANS_TAB, SCHEDULES_TAB, PROGRAMS_TAB, SETS_TAB, SESSIONS_TAB
            return {
                PLANS_TAB: plan_rows,
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
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        program_rows = [_program_row(1, "PPL", "Push", "Bench Press", plan_id=self.PLAN_ID)]
        side_effect = self._make_patch(plan_rows, schedule_rows, program_rows, [], [])
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.session_id is None
        assert result.is_completed is False

    def test_session_id_returned_when_session_exists(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        program_rows = [_program_row(1, "PPL", "Push", "Bench Press", plan_id=self.PLAN_ID)]
        session_rows = [_session_row(1, self._SESSION_ID, self._MONDAY)]
        side_effect = self._make_patch(plan_rows, schedule_rows, program_rows, [], session_rows)
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.session_id == self._SESSION_ID
        assert result.is_completed is False

    def test_is_completed_true_when_completed_at_set(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        program_rows = [_program_row(1, "PPL", "Push", "Bench Press", plan_id=self.PLAN_ID)]
        session_rows = [_session_row(1, self._SESSION_ID, self._MONDAY, completed_at="2026-06-08T11:00:00+00:00")]
        side_effect = self._make_patch(plan_rows, schedule_rows, program_rows, [], session_rows)
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.is_completed is True

    def test_plan_name_in_response(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "My PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        program_rows = [_program_row(1, "My PPL", "Push", "Bench Press", plan_id=self.PLAN_ID)]
        side_effect = self._make_patch(plan_rows, schedule_rows, program_rows, [], [])
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.plan_name == "My PPL"

    def test_sets_logged_today_counts_only_todays_sets(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        program_rows = [_program_row(1, "PPL", "Push", "Bench Press", plan_id=self.PLAN_ID)]
        set_rows = [
            _set_row(1, self._SESSION_ID, "Bench Press", set_number=1),
            _set_row(1, self._SESSION_ID, "Bench Press", set_number=2),
            _set_row(1, "1-2026-06-07", "Bench Press", set_number=1),  # previous session
        ]
        session_rows = [_session_row(1, self._SESSION_ID, self._MONDAY)]
        side_effect = self._make_patch(plan_rows, schedule_rows, program_rows, set_rows, session_rows)
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        bench = next(e for e in result.exercises if e.exercise_name == "Bench Press")
        assert bench.sets_logged_today == 2

    def test_rest_day_returns_no_session_state(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Rest", self.PLAN_ID)]
        side_effect = self._make_patch(plan_rows, schedule_rows, [], [], [])
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.is_rest_day is True
        assert result.session_id is None
        assert result.is_completed is False

    def test_legacy_fallback_no_plans_rows(self):
        """Legacy mode: no PLANS_TAB rows → filters by user_id only."""
        schedule_rows = [_schedule_row(1, 0, "Push", "")]  # no plan_id
        program_rows = [_program_row(1, "PPL", "Push", "Bench Press", plan_id="")]
        side_effect = self._make_patch([], schedule_rows, program_rows, [], [])
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date=self._MONDAY)
        assert result.is_rest_day is False
        assert len(result.exercises) == 1


# ---------------------------------------------------------------------------
# import_workout — non-destructive + schedule gap fill
# ---------------------------------------------------------------------------


class TestImportWorkoutNonDestructive:
    def _run_import(self, schedule: list[tuple[int, str]], existing_plan_rows: list = None):
        days = [WorkoutDaySummary(day_name="Push", exercises=[
            ExerciseInfo(exercise_name="Bench Press", sets=3, rep_min=8, rep_max=12, order=1),
        ])]
        written_schedule_rows: list[dict] = []
        written_program_rows: list[dict] = []
        appended_plan_rows: list[dict] = []

        def fake_safe_read(tab):
            from api.services.workout_service import PLANS_TAB
            if tab == PLANS_TAB:
                return existing_plan_rows or []
            return []

        def fake_append_row(tab, row):
            from api.services.workout_service import PLANS_TAB
            if tab == PLANS_TAB:
                appended_plan_rows.append(row)

        def fake_append_batch(tab, rows):
            from api.services.workout_service import SCHEDULES_TAB, PROGRAMS_TAB
            if tab == SCHEDULES_TAB:
                written_schedule_rows.extend(rows)
            elif tab == PROGRAMS_TAB:
                written_program_rows.extend(rows)

        def fake_update_row(tab, row_index, row):
            pass  # deactivation call

        with (
            patch("api.services.workout_service._safe_read_rows", side_effect=fake_safe_read),
            patch("api.services.workout_service.append_rows_batch", side_effect=fake_append_batch),
            patch("api.services.workout_service.append_row", side_effect=fake_append_row),
            patch("api.services.workout_service.update_row", side_effect=fake_update_row),
        ):
            import_workout(user_id=1, program_name="PPL", days=days, schedule=schedule)

        return written_schedule_rows, written_program_rows, appended_plan_rows

    def test_creates_new_plan_row(self):
        _, _, plan_rows = self._run_import([(0, "Push")])
        assert len(plan_rows) == 1
        assert plan_rows[0]["plan_name"] == "PPL"
        assert plan_rows[0]["is_active"] == "TRUE"

    def test_plan_row_contains_plan_id(self):
        _, _, plan_rows = self._run_import([(0, "Push")])
        assert "plan_id" in plan_rows[0]
        assert plan_rows[0]["plan_id"].startswith("1-")

    def test_program_rows_stamped_with_plan_id(self):
        _, program_rows, plan_rows = self._run_import([(0, "Push")])
        plan_id = plan_rows[0]["plan_id"]
        assert all(r["plan_id"] == plan_id for r in program_rows)

    def test_schedule_rows_stamped_with_plan_id(self):
        sched_rows, _, plan_rows = self._run_import([(0, "Push")])
        plan_id = plan_rows[0]["plan_id"]
        assert all(r["plan_id"] == plan_id for r in sched_rows)

    def test_all_7_weekdays_written_when_schedule_is_complete(self):
        full_schedule = [(i, "Push" if i < 5 else "Rest") for i in range(7)]
        sched_rows, _, _ = self._run_import(full_schedule)
        weekdays = {r["weekday"] for r in sched_rows}
        assert weekdays == set(range(7))

    def test_missing_weekdays_filled_with_rest(self):
        partial_schedule = [(0, "Push"), (2, "Pull")]
        sched_rows, _, _ = self._run_import(partial_schedule)
        weekdays = {r["weekday"] for r in sched_rows}
        assert weekdays == set(range(7))
        rest_weekdays = {r["weekday"] for r in sched_rows if r["day_name"] == "Rest"}
        assert rest_weekdays == {1, 3, 4, 5, 6}

    def test_empty_schedule_fills_all_7_as_rest(self):
        sched_rows, _, _ = self._run_import([])
        assert len(sched_rows) == 7
        assert all(r["day_name"] == "Rest" for r in sched_rows)

    def test_no_duplicate_weekdays(self):
        schedule = [(0, "Push"), (1, "Pull"), (2, "Legs"), (3, "Rest"), (4, "Push")]
        sched_rows, _, _ = self._run_import(schedule)
        weekdays = [r["weekday"] for r in sched_rows]
        assert len(weekdays) == len(set(weekdays)), "duplicate weekdays written"


# ---------------------------------------------------------------------------
# list_plans
# ---------------------------------------------------------------------------


class TestListPlans:
    PLAN_A = "1-100"
    PLAN_B = "1-200"

    def test_returns_all_user_plans(self):
        plan_rows = [
            _plan_row(1, self.PLAN_A, "PPL", is_active=True),
            _plan_row(1, self.PLAN_B, "Cut", is_active=False),
        ]
        program_rows = [
            _program_row(1, "PPL", "Push", "Bench Press", plan_id=self.PLAN_A),
            _program_row(1, "Cut", "Full Body", "Squat", plan_id=self.PLAN_B),
        ]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=[plan_rows, program_rows]):
            result = list_plans(user_id=1)
        assert len(result.plans) == 2
        names = {p.plan_name for p in result.plans}
        assert names == {"PPL", "Cut"}

    def test_active_flag_correct(self):
        plan_rows = [
            _plan_row(1, self.PLAN_A, "PPL", is_active=True),
            _plan_row(1, self.PLAN_B, "Cut", is_active=False),
        ]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=[plan_rows, []]):
            result = list_plans(user_id=1)
        active = next(p for p in result.plans if p.plan_name == "PPL")
        inactive = next(p for p in result.plans if p.plan_name == "Cut")
        assert active.is_active is True
        assert inactive.is_active is False

    def test_exercise_count_per_plan(self):
        plan_rows = [_plan_row(1, self.PLAN_A, "PPL", is_active=True)]
        program_rows = [
            _program_row(1, "PPL", "Push", "Bench Press", plan_id=self.PLAN_A),
            _program_row(1, "PPL", "Push", "OHP", plan_id=self.PLAN_A),
            _program_row(1, "PPL", "Pull", "Row", plan_id=self.PLAN_A),
        ]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=[plan_rows, program_rows]):
            result = list_plans(user_id=1)
        ppl = result.plans[0]
        assert ppl.exercise_count == 3
        assert ppl.day_count == 2  # Push, Pull

    def test_ignores_other_users_plans(self):
        plan_rows = [
            _plan_row(1, self.PLAN_A, "PPL", is_active=True),
            _plan_row(2, "2-100", "Other", is_active=True),
        ]
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=[plan_rows, []]):
            result = list_plans(user_id=1)
        assert len(result.plans) == 1
        assert result.plans[0].plan_name == "PPL"

    def test_empty_returns_empty_list(self):
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=[[], []]):
            result = list_plans(user_id=1)
        assert result.plans == []


# ---------------------------------------------------------------------------
# activate_plan
# ---------------------------------------------------------------------------


class TestActivatePlan:
    PLAN_A = "1-100"
    PLAN_B = "1-200"

    def test_activates_target_plan(self):
        plan_rows = [
            _plan_row(1, self.PLAN_A, "PPL", is_active=True),
            _plan_row(1, self.PLAN_B, "Cut", is_active=False),
        ]
        updated_rows: list[dict] = []

        def fake_update(tab, row_index, row):
            updated_rows.append(dict(row))

        with (
            patch("api.services.workout_service._safe_read_rows", return_value=plan_rows),
            patch("api.services.workout_service.update_row", side_effect=fake_update),
        ):
            activate_plan(user_id=1, plan_id=self.PLAN_B)

        # Plan B should now be TRUE, Plan A should be FALSE
        b_row = next(r for r in updated_rows if r.get("plan_id") == self.PLAN_B)
        a_row = next(r for r in updated_rows if r.get("plan_id") == self.PLAN_A)
        assert b_row["is_active"] == "TRUE"
        assert a_row["is_active"] == "FALSE"

    def test_raises_when_plan_not_found(self):
        plan_rows = [_plan_row(1, self.PLAN_A, "PPL", is_active=True)]
        with (
            patch("api.services.workout_service._safe_read_rows", return_value=plan_rows),
            patch("api.services.workout_service.update_row"),
        ):
            with pytest.raises(ValueError, match="not found"):
                activate_plan(user_id=1, plan_id="nonexistent")


# ---------------------------------------------------------------------------
# delete_plan
# ---------------------------------------------------------------------------


class TestDeletePlan:
    PLAN_A = "1-100"
    PLAN_B = "1-200"

    def test_raises_when_deleting_active_plan(self):
        plan_rows = [_plan_row(1, self.PLAN_A, "PPL", is_active=True)]
        with patch("api.services.workout_service._safe_read_rows", return_value=plan_rows):
            with pytest.raises(ValueError, match="active plan"):
                delete_plan(user_id=1, plan_id=self.PLAN_A)

    def test_raises_when_plan_not_found(self):
        plan_rows = [_plan_row(1, self.PLAN_A, "PPL", is_active=True)]
        # First call (get_active_plan_id) returns active plan; second call (list for idx) also
        with patch("api.services.workout_service._safe_read_rows", return_value=plan_rows):
            with pytest.raises(ValueError, match="not found"):
                delete_plan(user_id=1, plan_id=self.PLAN_B)

    def test_deletes_plan_rows_and_plan_entry(self):
        plan_rows_for_get_active = [_plan_row(1, self.PLAN_A, "PPL", is_active=True)]
        plan_rows_for_idx = [
            _plan_row(1, self.PLAN_A, "PPL", is_active=True),
            _plan_row(1, self.PLAN_B, "Cut", is_active=False),
        ]
        call_count = {"n": 0}

        def fake_safe_read(tab):
            call_count["n"] += 1
            if call_count["n"] == 1:  # get_active_plan_id
                return plan_rows_for_get_active
            return plan_rows_for_idx  # second read for plan index lookup

        deleted_tabs: list[str] = []

        def fake_delete_plan_rows(tab, uid, pid):
            deleted_tabs.append(tab)

        mock_ws = MagicMock()

        with (
            patch("api.services.workout_service._safe_read_rows", side_effect=fake_safe_read),
            patch("api.services.workout_service._delete_plan_rows", side_effect=fake_delete_plan_rows),
            patch("api.services.workout_service.get_worksheet", return_value=mock_ws),
        ):
            delete_plan(user_id=1, plan_id=self.PLAN_B)

        from api.services.workout_service import PROGRAMS_TAB, SCHEDULES_TAB
        assert PROGRAMS_TAB in deleted_tabs
        assert SCHEDULES_TAB in deleted_tabs
        mock_ws.delete_rows.assert_called_once()


# ---------------------------------------------------------------------------
# Robustness: rows with missing / empty exercise_name in WorkoutPrograms
# ---------------------------------------------------------------------------


class TestMissingExerciseNameRows:
    """get_schedule and get_today_workout must never crash on rows that have
    exercise_name missing or empty — they should silently skip those rows."""

    PLAN_ID = "1-abc"

    def _make_today_patch(self, plan_rows, schedule_rows, program_rows, set_rows=None, session_rows=None):
        def side_effect(tab):
            from api.services.workout_service import PLANS_TAB, SCHEDULES_TAB, PROGRAMS_TAB, SETS_TAB, SESSIONS_TAB
            return {
                PLANS_TAB: plan_rows,
                SCHEDULES_TAB: schedule_rows,
                PROGRAMS_TAB: program_rows,
                SETS_TAB: set_rows or [],
                SESSIONS_TAB: session_rows or [],
            }[tab]
        return side_effect

    def _make_schedule_patch(self, plan_rows, schedule_rows, program_rows):
        def side_effect(tab):
            from api.services.workout_service import PLANS_TAB, SCHEDULES_TAB, PROGRAMS_TAB
            return {
                PLANS_TAB: plan_rows,
                SCHEDULES_TAB: schedule_rows,
                PROGRAMS_TAB: program_rows,
            }[tab]
        return side_effect

    def test_get_schedule_skips_row_with_missing_exercise_name_key(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        bad_row = {"user_id": 1, "plan_id": self.PLAN_ID, "program_name": "PPL", "day_name": "Push",
                   "sets": 3, "rep_min": 8, "rep_max": 12, "order": 1, "created_at": ""}
        good_row = _program_row(1, "PPL", "Push", "Bench Press", order=2, plan_id=self.PLAN_ID)
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_schedule_patch(plan_rows, schedule_rows, [bad_row, good_row])):
            result = get_schedule(user_id=1)
        monday = result.days[0]
        assert len(monday.exercises) == 1
        assert monday.exercises[0].exercise_name == "Bench Press"

    def test_get_schedule_skips_row_with_empty_exercise_name(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        empty_name_row = _program_row(1, "PPL", "Push", "", order=1, plan_id=self.PLAN_ID)
        good_row = _program_row(1, "PPL", "Push", "OHP", order=2, plan_id=self.PLAN_ID)
        with patch("api.services.workout_service._safe_read_rows",
                   side_effect=self._make_schedule_patch(plan_rows, schedule_rows, [empty_name_row, good_row])):
            result = get_schedule(user_id=1)
        monday = result.days[0]
        assert len(monday.exercises) == 1
        assert monday.exercises[0].exercise_name == "OHP"

    def test_get_today_workout_skips_row_with_empty_exercise_name(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        empty_name_row = _program_row(1, "PPL", "Push", "", order=1, plan_id=self.PLAN_ID)
        good_row = _program_row(1, "PPL", "Push", "Squat", order=2, plan_id=self.PLAN_ID)
        side_effect = self._make_today_patch(plan_rows, schedule_rows, [empty_name_row, good_row])
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date="2026-06-08")
        assert len(result.exercises) == 1
        assert result.exercises[0].exercise_name == "Squat"

    def test_get_today_workout_all_bad_rows_returns_no_exercises(self):
        plan_rows = [_plan_row(1, self.PLAN_ID, "PPL", is_active=True)]
        schedule_rows = [_schedule_row(1, 0, "Push", self.PLAN_ID)]
        bad_rows = [_program_row(1, "PPL", "Push", "", order=1, plan_id=self.PLAN_ID)]
        side_effect = self._make_today_patch(plan_rows, schedule_rows, bad_rows)
        with patch("api.services.workout_service._safe_read_rows", side_effect=side_effect):
            result = get_today_workout(user_id=1, today_date="2026-06-08")
        assert result.exercises == []
        assert result.is_rest_day is False
