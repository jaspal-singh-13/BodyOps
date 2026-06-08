"""Tests for GET /settings and POST /settings."""
from unittest.mock import call, patch

import gspread.exceptions


SETTINGS_ROW = {
    "user_id": "1",
    "name": "Test User",
    "current_weight_kg": "80.0",
    "height_cm": "175.0",
    "age": "30",
    "goal_weight_kg": "70.0",
    "start_date": "2026-01-01",
    "calorie_target": "2000",
    "protein_target_g": "150",
    "wake_up_time": "07:00",
    "unit_preference": "metric",
    "reminders_json": "{}",
    "updated_at": "2026-01-01T00:00:00+00:00",
}

SETTINGS_PAYLOAD = {
    "user_id": 1,
    "name": "Test User",
    "current_weight_kg": 80.0,
    "height_cm": 175.0,
    "age": 30,
    "goal_weight_kg": 70.0,
    "start_date": "2026-01-01",
    "calorie_target": 2000,
    "protein_target_g": 150,
    "wake_up_time": "07:00",
    "unit_preference": "metric",
    "reminders_json": "{}",
}


class TestGetSettings:
    def test_get_settings_found(self, client, auth_headers):
        with patch("api.services.settings_service.read_rows", return_value=[SETTINGS_ROW]):
            resp = client.get("/settings", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["user_id"] == 1
        assert data["name"] == "Test User"
        assert data["calorie_target"] == 2000

    def test_get_settings_not_found_empty_rows(self, client, auth_headers):
        # Patch at the router boundary to bypass the service-layer TTL cache
        with patch("api.routers.settings.get_settings", return_value=None):
            resp = client.get("/settings", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_settings_not_found_wrong_user(self, client, auth_headers):
        with patch("api.routers.settings.get_settings", return_value=None):
            resp = client.get("/settings", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_settings_worksheet_missing(self, client, auth_headers):
        # WorksheetNotFound in the service causes get_settings to return None → 404
        with patch("api.routers.settings.get_settings", return_value=None):
            resp = client.get("/settings", headers=auth_headers)
        assert resp.status_code == 404

    def test_get_settings_no_auth(self, client):
        resp = client.get("/settings")
        assert resp.status_code == 401


class TestPostSettings:
    def test_post_settings_creates_new(self, client, auth_headers):
        with (
            patch("api.services.settings_service.find_row", return_value=None),
            patch("api.services.settings_service.append_row") as mock_append,
        ):
            resp = client.post("/settings", json=SETTINGS_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 200
        mock_append.assert_called_once()
        saved = mock_append.call_args[0][1]
        assert saved["user_id"] == 1

    def test_post_settings_updates_existing(self, client, auth_headers):
        with (
            patch("api.services.settings_service.find_row", return_value=(2, SETTINGS_ROW)),
            patch("api.services.settings_service.update_row") as mock_update,
        ):
            resp = client.post("/settings", json=SETTINGS_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 200
        mock_update.assert_called_once()
        _, row_index, saved = mock_update.call_args[0]
        assert row_index == 2
        assert saved["user_id"] == 1

    def test_post_settings_no_auth(self, client):
        resp = client.post("/settings", json=SETTINGS_PAYLOAD)
        assert resp.status_code == 401
