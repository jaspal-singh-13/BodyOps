"""Unit tests for api/services/task_service.py."""

import os

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-id")

from unittest.mock import MagicMock, call, patch

import pytest

# ---------------------------------------------------------------------------
# Fixtures / shared data
# ---------------------------------------------------------------------------

from datetime import date as _date

USER_ID = 1
TODAY = _date.today().isoformat()
TODAY_WEEKDAY = str(_date.today().weekday())

TASK_ROWS = [
    {"user_id": "1", "id": "task-1", "name": "Log your weight", "description": "Weigh in", "task_type": "log_weight"},
    {"user_id": "1", "id": "task-2", "name": "Hit protein target", "description": "Protein goal", "task_type": "hit_protein"},
    {"user_id": "1", "id": "task-3", "name": "Stay under calorie target", "description": "Calorie goal", "task_type": "stay_under_calories"},
    {"user_id": "1", "id": "task-4", "name": "Complete today's workout", "description": "Workout", "task_type": "complete_workout"},
    {"user_id": "1", "id": "task-5", "name": "Drink enough water", "description": "Hydrate", "task_type": "drink_water"},
]

STATUS_ROWS = [
    {"user_id": "1", "id": "ds-1", "task_id": "task-1", "date": TODAY, "completed": "FALSE", "completed_at": ""},
    {"user_id": "1", "id": "ds-2", "task_id": "task-2", "date": TODAY, "completed": "FALSE", "completed_at": ""},
    {"user_id": "1", "id": "ds-3", "task_id": "task-3", "date": TODAY, "completed": "FALSE", "completed_at": ""},
    {"user_id": "1", "id": "ds-4", "task_id": "task-4", "date": TODAY, "completed": "FALSE", "completed_at": ""},
    {"user_id": "1", "id": "ds-5", "task_id": "task-5", "date": TODAY, "completed": "FALSE", "completed_at": ""},
]


# ---------------------------------------------------------------------------
# get_today_tasks
# ---------------------------------------------------------------------------

class TestGetTodayTasks:
    def test_returns_all_tasks_for_workout_day(self):
        """Returns 5 tasks when today is a workout day."""
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.append_rows_batch"),
        ):
            # Tasks exist; status rows exist; workout day (non-rest)
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": STATUS_ROWS,
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import get_today_tasks
            result = get_today_tasks(USER_ID, "UTC")

        assert result.total == 5
        assert result.completed == 0
        assert result.percentage == 0.0
        assert result.date == TODAY
        assert len(result.tasks) == 5

    def test_omits_workout_task_on_rest_day(self):
        """complete_workout task is excluded on rest days."""
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.append_rows_batch"),
        ):
            # Workout schedule says rest
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": [r for r in STATUS_ROWS if r["task_id"] != "task-4"],
                "WorkoutSchedules": [{"user_id": "1", "weekday": "2", "day_name": "Rest"}],
            }.get(tab, [])

            from api.services.task_service import get_today_tasks
            result = get_today_tasks(USER_ID, "UTC")

        task_types = [t.task_type for t in result.tasks]
        assert "complete_workout" not in task_types
        assert result.total == 4

    def test_percentage_reflects_completed_tasks(self):
        """percentage is computed correctly when some tasks are done."""
        done_status = [
            {**r, "completed": "TRUE", "completed_at": "2026-06-11T08:00:00+00:00"}
            if r["task_id"] == "task-1"
            else r
            for r in STATUS_ROWS
        ]
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.append_rows_batch"),
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": done_status,
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import get_today_tasks
            result = get_today_tasks(USER_ID, "UTC")

        assert result.completed == 1
        assert result.percentage == 20.0


# ---------------------------------------------------------------------------
# generate_daily_tasks idempotency
# ---------------------------------------------------------------------------

class TestGenerateDailyTasksIdempotency:
    def test_does_not_duplicate_rows_when_called_twice(self):
        """DailyTaskStatus rows are not appended a second time if they already exist."""
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.append_rows_batch") as mock_append,
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": STATUS_ROWS,  # already exists
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import _ensure_daily_status
            _ensure_daily_status(USER_ID, TODAY, TASK_ROWS)

        # All task_ids are already present → nothing should be appended
        mock_append.assert_not_called()

    def test_appends_rows_when_none_exist(self):
        """DailyTaskStatus rows are created when the date has no entries."""
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.append_rows_batch") as mock_append,
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": [],  # empty
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import _ensure_daily_status
            _ensure_daily_status(USER_ID, TODAY, TASK_ROWS)

        mock_append.assert_called_once()
        appended_rows = mock_append.call_args[0][1]
        assert len(appended_rows) == 5  # all 5 tasks


# ---------------------------------------------------------------------------
# complete_task
# ---------------------------------------------------------------------------

class TestCompleteTask:
    def test_marks_task_completed_and_sets_timestamp(self):
        """complete_task updates the correct row with completed=TRUE."""
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.update_row") as mock_update,
            patch("api.services.task_service.append_rows_batch"),
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": STATUS_ROWS,
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import complete_task
            result = complete_task(USER_ID, "task-1", TODAY)

        mock_update.assert_called_once()
        updated_row = mock_update.call_args[0][2]
        assert updated_row["completed"] == "TRUE"
        assert updated_row["completed_at"] != ""

    def test_no_op_if_already_completed(self):
        """complete_task does not write if task is already done."""
        done_status = [
            {**r, "completed": "TRUE", "completed_at": "2026-06-11T08:00:00+00:00"}
            if r["task_id"] == "task-1"
            else r
            for r in STATUS_ROWS
        ]
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.update_row") as mock_update,
            patch("api.services.task_service.append_rows_batch"),
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": done_status,
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import complete_task
            result = complete_task(USER_ID, "task-1", TODAY)

        mock_update.assert_not_called()

    def test_returns_updated_status_response(self):
        """complete_task returns DailyStatusResponse with updated counts."""
        done_status = [
            {**r, "completed": "TRUE", "completed_at": "2026-06-11T08:00:00+00:00"}
            if r["task_id"] == "task-1"
            else r
            for r in STATUS_ROWS
        ]
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.update_row"),
            patch("api.services.task_service.append_rows_batch"),
        ):
            # After update the read returns updated state
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": done_status,
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import complete_task
            result = complete_task(USER_ID, "task-1", TODAY)

        assert result.completed == 1
        assert result.total == 5


# ---------------------------------------------------------------------------
# auto_complete_task
# ---------------------------------------------------------------------------

class TestAutoCompleteTask:
    def test_no_op_if_task_already_completed(self):
        """auto_complete_task does not write if the task is already marked done."""
        done_status = [
            {**r, "completed": "TRUE", "completed_at": "2026-06-11T08:00:00+00:00"}
            if r["task_id"] == "task-1"
            else r
            for r in STATUS_ROWS
        ]
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.update_row") as mock_update,
            patch("api.services.task_service.append_rows_batch"),
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": done_status,
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import auto_complete_task
            auto_complete_task(USER_ID, "log_weight", TODAY)

        mock_update.assert_not_called()

    def test_completes_task_when_not_yet_done(self):
        """auto_complete_task writes completed=TRUE when task is pending."""
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.update_row") as mock_update,
            patch("api.services.task_service.append_rows_batch"),
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": STATUS_ROWS,
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import auto_complete_task
            auto_complete_task(USER_ID, "log_weight", TODAY)

        mock_update.assert_called_once()
        updated = mock_update.call_args[0][2]
        assert updated["completed"] == "TRUE"

    def test_no_op_if_no_task_definition(self):
        """auto_complete_task silently does nothing when task_type has no definition."""
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.update_row") as mock_update,
            patch("api.services.task_service.append_rows_batch"),
        ):
            mock_read.return_value = []

            from api.services.task_service import auto_complete_task
            auto_complete_task(USER_ID, "nonexistent_type", TODAY)

        mock_update.assert_not_called()


# ---------------------------------------------------------------------------
# check_nutrition_targets
# ---------------------------------------------------------------------------

class TestCheckNutritionTargets:
    def test_completes_protein_task_when_target_met(self):
        """check_nutrition_targets completes hit_protein when consumed >= target."""
        from api.models.meal import DailyNutrition
        from api.models.settings import SettingsResponse

        mock_nutrition = DailyNutrition(
            date=TODAY,
            calories=1800,
            protein_g=160,  # >= target of 150
            carbs_g=200,
            fat_g=60,
            target_calories=2000,
            target_protein_g=150,
            target_carbs_g=250,
            target_fat_g=65,
            meals_count=3,
        )
        mock_settings = SettingsResponse(
            user_id=USER_ID, name="Test", current_weight_kg=85.0,
            height_cm=175.0, age=30, goal_weight_kg=77.0,
            start_date="2026-01-01", calorie_target=2000,
            protein_target_g=150, wake_up_time="07:00",
        )

        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.update_row") as mock_update,
            patch("api.services.task_service.append_rows_batch"),
            patch("api.services.meal_service.get_meals_today", return_value=mock_nutrition),
            patch("api.services.settings_service.get_settings", return_value=mock_settings),
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": STATUS_ROWS,
                "WorkoutSchedules": [],
            }.get(tab, [])

            from api.services.task_service import check_nutrition_targets
            check_nutrition_targets(USER_ID, "UTC")

        # Should have updated the hit_protein task row
        assert mock_update.call_count >= 1
        updated_rows = [c[0][2] for c in mock_update.call_args_list]
        task_ids_updated = {r.get("task_id") for r in updated_rows}
        assert "task-2" in task_ids_updated  # hit_protein

    def test_does_not_complete_protein_task_when_below_target(self):
        """check_nutrition_targets does not complete hit_protein when under target."""
        from api.models.meal import DailyNutrition
        from api.models.settings import SettingsResponse

        mock_nutrition = DailyNutrition(
            date=TODAY,
            calories=1400,
            protein_g=80,  # < target of 150
            carbs_g=150,
            fat_g=40,
            target_calories=2000,
            target_protein_g=150,
            target_carbs_g=250,
            target_fat_g=65,
            meals_count=2,
        )
        mock_settings = SettingsResponse(
            user_id=USER_ID, name="Test", current_weight_kg=85.0,
            height_cm=175.0, age=30, goal_weight_kg=77.0,
            start_date="2026-01-01", calorie_target=2000,
            protein_target_g=150, wake_up_time="07:00",
        )

        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.update_row") as mock_update,
            patch("api.services.task_service.append_rows_batch"),
            patch("api.services.meal_service.get_meals_today", return_value=mock_nutrition),
            patch("api.services.settings_service.get_settings", return_value=mock_settings),
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": STATUS_ROWS,
                "WorkoutSchedules": [],
            }.get(tab, [])

            from api.services.task_service import check_nutrition_targets
            check_nutrition_targets(USER_ID, "UTC")

        # hit_protein (task-2) should NOT be updated
        if mock_update.called:
            updated_task_ids = {c[0][2].get("task_id") for c in mock_update.call_args_list}
            assert "task-2" not in updated_task_ids


# ---------------------------------------------------------------------------
# get_status
# ---------------------------------------------------------------------------

class TestGetStatus:
    def test_returns_correct_totals(self):
        """get_status returns correct total, completed, and percentage fields."""
        done_status = [
            {**r, "completed": "TRUE", "completed_at": "2026-06-11T08:00:00+00:00"}
            if r["task_id"] in {"task-1", "task-2", "task-3"}
            else r
            for r in STATUS_ROWS
        ]
        with (
            patch("api.services.task_service.read_rows") as mock_read,
            patch("api.services.task_service.append_rows_batch"),
        ):
            mock_read.side_effect = lambda tab: {
                "Tasks": TASK_ROWS,
                "DailyTaskStatus": done_status,
                "WorkoutSchedules": [{"user_id": "1", "weekday": TODAY_WEEKDAY, "day_name": "Push"}],
            }.get(tab, [])

            from api.services.task_service import get_status
            result = get_status(USER_ID, "UTC")

        assert result.total == 5
        assert result.completed == 3
        assert result.percentage == 60.0
