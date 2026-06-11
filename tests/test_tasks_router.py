"""Integration tests for GET /tasks/today, POST /tasks/complete, GET /tasks/status."""

from unittest.mock import patch

from api.models.task import DailyStatusResponse, TaskResponse

TODAY = "2026-06-11"

_TASK_ITEM = TaskResponse(
    id="task-1",
    name="Log your weight",
    description="Weigh in",
    task_type="log_weight",
    completed=False,
    completed_at=None,
)

DAILY_RESPONSE = DailyStatusResponse(
    date=TODAY,
    tasks=[_TASK_ITEM],
    total=1,
    completed=0,
    percentage=0.0,
)

DAILY_RESPONSE_COMPLETED = DailyStatusResponse(
    date=TODAY,
    tasks=[
        TaskResponse(
            id="task-1",
            name="Log your weight",
            description="Weigh in",
            task_type="log_weight",
            completed=True,
            completed_at="2026-06-11T08:00:00+00:00",
        )
    ],
    total=1,
    completed=1,
    percentage=100.0,
)


class TestGetTodayTasks:
    def test_returns_200_with_task_list(self, client, auth_headers):
        with patch("api.routers.tasks.get_today_tasks", return_value=DAILY_RESPONSE):
            resp = client.get("/tasks/today", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "tasks" in data
        assert "total" in data
        assert "completed" in data
        assert "percentage" in data
        assert data["date"] == TODAY

    def test_returns_401_without_auth(self, client):
        resp = client.get("/tasks/today")
        assert resp.status_code == 401

    def test_task_fields_present(self, client, auth_headers):
        with patch("api.routers.tasks.get_today_tasks", return_value=DAILY_RESPONSE):
            resp = client.get("/tasks/today", headers=auth_headers)
        tasks = resp.json()["tasks"]
        assert len(tasks) == 1
        t = tasks[0]
        assert "id" in t
        assert "name" in t
        assert "task_type" in t
        assert "completed" in t


class TestCompleteTask:
    def test_returns_200_with_updated_status(self, client, auth_headers):
        with patch("api.routers.tasks.complete_task", return_value=DAILY_RESPONSE_COMPLETED):
            resp = client.post(
                "/tasks/complete",
                json={"task_id": "task-1", "date": TODAY},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["completed"] == 1
        assert data["percentage"] == 100.0

    def test_returns_401_without_auth(self, client):
        resp = client.post("/tasks/complete", json={"task_id": "task-1", "date": TODAY})
        assert resp.status_code == 401

    def test_returns_422_missing_task_id(self, client, auth_headers):
        resp = client.post(
            "/tasks/complete",
            json={"date": TODAY},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_returns_422_missing_date(self, client, auth_headers):
        resp = client.post(
            "/tasks/complete",
            json={"task_id": "task-1"},
            headers=auth_headers,
        )
        assert resp.status_code == 422

    def test_returns_422_invalid_date_format(self, client, auth_headers):
        resp = client.post(
            "/tasks/complete",
            json={"task_id": "task-1", "date": "11-06-2026"},
            headers=auth_headers,
        )
        assert resp.status_code == 422


class TestGetStatus:
    def test_returns_200_with_summary_fields(self, client, auth_headers):
        with patch("api.routers.tasks.get_status", return_value=DAILY_RESPONSE):
            resp = client.get("/tasks/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total" in data
        assert "completed" in data
        assert "percentage" in data

    def test_returns_401_without_auth(self, client):
        resp = client.get("/tasks/status")
        assert resp.status_code == 401
