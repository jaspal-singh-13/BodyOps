"""Tests for POST /weight, GET /weight/history, GET /weight/trend."""
from unittest.mock import patch

from api.models.weight import WeightEntryResponse, WeightHistoryItem, WeightTrendResponse
from api.models.settings import SettingsResponse

WEIGHT_PAYLOAD = {"date": "2026-06-08", "weight_kg": 85.5}

WEIGHT_RESPONSE = WeightEntryResponse(
    user_id=1,
    date="2026-06-08",
    time="10:00",
    weight_kg=85.5,
    logged_at="2026-06-08T10:00:00+00:00",
)

HISTORY_RESPONSE = [
    WeightHistoryItem(date="2026-06-08", time="10:00", weight_kg=85.5, change_kg=-0.5),
    WeightHistoryItem(date="2026-06-07", time="08:00", weight_kg=86.0, change_kg=None),
]

TREND_RESPONSE = WeightTrendResponse(
    moving_avg=[{"date": "2026-06-08", "weight_kg": 85.5, "ma_7": None}],
    total_loss_kg=None,
    projected_goal_date=None,
)

SETTINGS_RESPONSE = SettingsResponse(
    user_id=1,
    name="Test User",
    current_weight_kg=85.5,
    height_cm=175.0,
    age=30,
    goal_weight_kg=77.0,
    start_date="2026-01-01",
    calorie_target=2000,
    protein_target_g=150,
    wake_up_time="07:00",
)


class TestPostWeight:
    def test_log_weight_success(self, client, auth_headers):
        with patch("api.routers.weight.log_weight", return_value=WEIGHT_RESPONSE):
            resp = client.post("/weight", json=WEIGHT_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["date"] == "2026-06-08"
        assert data["weight_kg"] == 85.5
        assert data["user_id"] == 1

    def test_log_weight_no_auth_returns_401(self, client):
        resp = client.post("/weight", json=WEIGHT_PAYLOAD)
        assert resp.status_code == 401

    def test_log_weight_missing_date_returns_422(self, client, auth_headers):
        resp = client.post("/weight", json={"weight_kg": 85.5}, headers=auth_headers)
        assert resp.status_code == 422

    def test_log_weight_missing_weight_returns_422(self, client, auth_headers):
        resp = client.post("/weight", json={"date": "2026-06-08"}, headers=auth_headers)
        assert resp.status_code == 422

    def test_log_weight_invalid_weight_type_returns_422(self, client, auth_headers):
        resp = client.post("/weight", json={"date": "2026-06-08", "weight_kg": "heavy"}, headers=auth_headers)
        assert resp.status_code == 422


class TestGetHistory:
    def test_get_history_returns_list(self, client, auth_headers):
        with patch("api.routers.weight.get_history", return_value=HISTORY_RESPONSE):
            resp = client.get("/weight/history", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["date"] == "2026-06-08"

    def test_get_history_empty_returns_empty_list(self, client, auth_headers):
        with patch("api.routers.weight.get_history", return_value=[]):
            resp = client.get("/weight/history", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_history_no_auth_returns_401(self, client):
        resp = client.get("/weight/history")
        assert resp.status_code == 401


class TestGetTrend:
    def test_get_trend_returns_structure(self, client, auth_headers):
        with (
            patch("api.routers.weight.get_settings", return_value=SETTINGS_RESPONSE),
            patch("api.routers.weight.get_trend", return_value=TREND_RESPONSE),
        ):
            resp = client.get("/weight/trend", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "moving_avg" in data
        assert "total_loss_kg" in data
        assert "projected_goal_date" in data

    def test_get_trend_no_settings_returns_404(self, client, auth_headers):
        with patch("api.routers.weight.get_settings", return_value=None):
            resp = client.get("/weight/trend", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_trend_no_auth_returns_401(self, client):
        resp = client.get("/weight/trend")
        assert resp.status_code == 401
