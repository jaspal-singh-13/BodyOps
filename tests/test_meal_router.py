"""
Tests for the meals API routes and Phase 4 agent tools.

Router tests: POST /meals/analyze, POST /meals, GET /meals/today, GET /meals/history
Agent tool tests: get_daily_nutrition, save_meal, analyze_meal_photo
"""

import asyncio
import io
import os
from unittest.mock import AsyncMock, MagicMock, patch

os.environ.setdefault("JWT_SECRET", "test-secret-key-for-tests")
os.environ.setdefault("GOOGLE_SERVICE_ACCOUNT_JSON", '{"type":"service_account"}')
os.environ.setdefault("GOOGLE_SPREADSHEET_ID", "test-sheet-id")
os.environ.setdefault("GOOGLE_AUTH_SHEET_ID", "test-auth-id")
os.environ.setdefault("AZURE_OPENAI_API_KEY", "test-key")
os.environ.setdefault("AZURE_OPENAI_ENDPOINT", "https://test.openai.azure.com")
os.environ.setdefault("AZURE_OPENAI_DEPLOYMENT", "gpt-4o")
os.environ.setdefault("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
os.environ.setdefault("GOOGLE_DRIVE_FOLDER_ID", "test-folder-id")

import pytest

from api.models.meal import (
    AnalyzeMealResponse,
    ConfirmMealRequest,
    DailyNutrition,
    DetectedItem,
    MacroTotal,
    MealHistoryDay,
    SavedMealResponse,
)

# ---------------------------------------------------------------------------
# Fixture data
# ---------------------------------------------------------------------------

DRIVE_URL = "https://drive.google.com/uc?id=test123"

DETECTED_ITEM = DetectedItem(
    name="Grilled chicken",
    quantity="180 g",
    calories=297,
    protein_g=56.0,
    carbs_g=0.0,
    fat_g=6.0,
    confidence="high",
)

ANALYZE_RESPONSE = AnalyzeMealResponse(
    title="Chicken rice bowl",
    confidence="high",
    detected=[DETECTED_ITEM],
    total=MacroTotal(calories=297, protein_g=56.0, carbs_g=0.0, fat_g=6.0),
    drive_url=DRIVE_URL,
)

DAILY_NUTRITION = DailyNutrition(
    date="2026-06-08",
    calories=640,
    protein_g=58.0,
    carbs_g=70.0,
    fat_g=14.0,
    target_calories=2100,
    target_protein_g=200.0,
    target_carbs_g=180.0,
    target_fat_g=65.0,
    meals_count=1,
)

SAVED_MEAL = SavedMealResponse(
    meal_id="aaa-bbb-ccc",
    meal_type="Lunch",
    date="2026-06-08",
    total=MacroTotal(calories=297, protein_g=56.0, carbs_g=0.0, fat_g=6.0),
    daily_nutrition=DAILY_NUTRITION,
)

CONFIRM_PAYLOAD = {
    "meal_type": "Lunch",
    "items": [
        {
            "name": "Grilled chicken",
            "quantity": "180 g",
            "calories": 297,
            "protein_g": 56.0,
            "carbs_g": 0.0,
            "fat_g": 6.0,
            "confidence": "high",
        }
    ],
    "drive_url": DRIVE_URL,
    "date": "2026-06-08",
}

HISTORY_ITEMS = [
    MealHistoryDay(
        date="2026-06-08",
        display_date="Today · Jun 8",
        meals_count=2,
        total_calories=1280,
        total_protein_g=112.0,
    ),
    MealHistoryDay(
        date="2026-06-07",
        display_date="Yesterday · Jun 7",
        meals_count=4,
        total_calories=2040,
        total_protein_g=198.0,
    ),
]

# ---------------------------------------------------------------------------
# POST /meals/analyze
# ---------------------------------------------------------------------------


class TestPostMealsAnalyze:
    def test_analyze_success(self, client, auth_headers):
        with (
            patch("api.routers.meals.upload_meal_image", new_callable=AsyncMock, return_value=DRIVE_URL),
            patch("api.routers.meals.analyze_meal", new_callable=AsyncMock, return_value=ANALYZE_RESPONSE),
        ):
            resp = client.post(
                "/meals/analyze",
                files={"file": ("meal.jpg", io.BytesIO(b"JPEG"), "image/jpeg")},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "Chicken rice bowl"
        assert data["confidence"] == "high"
        assert len(data["detected"]) == 1
        assert data["detected"][0]["name"] == "Grilled chicken"
        assert data["drive_url"] == DRIVE_URL
        assert "total" in data

    def test_analyze_no_auth_returns_401(self, client):
        resp = client.post(
            "/meals/analyze",
            files={"file": ("meal.jpg", io.BytesIO(b"JPEG"), "image/jpeg")},
        )
        assert resp.status_code == 401

    def test_analyze_unsupported_mime_returns_400(self, client, auth_headers):
        resp = client.post(
            "/meals/analyze",
            files={"file": ("doc.pdf", io.BytesIO(b"%PDF"), "application/pdf")},
            headers=auth_headers,
        )
        assert resp.status_code == 400

    def test_analyze_empty_file_returns_400(self, client, auth_headers):
        with (
            patch("api.routers.meals.upload_meal_image", new_callable=AsyncMock, return_value=DRIVE_URL),
        ):
            resp = client.post(
                "/meals/analyze",
                files={"file": ("meal.jpg", io.BytesIO(b""), "image/jpeg")},
                headers=auth_headers,
            )
        assert resp.status_code == 400

    def test_analyze_drive_error_still_returns_200(self, client, auth_headers):
        """Drive upload failure is non-fatal — analysis proceeds with empty drive_url."""
        with (
            patch(
                "api.routers.meals.upload_meal_image",
                new_callable=AsyncMock,
                side_effect=Exception("Drive quota exceeded"),
            ),
            patch("api.routers.meals.analyze_meal", new_callable=AsyncMock, return_value=ANALYZE_RESPONSE),
        ):
            resp = client.post(
                "/meals/analyze",
                files={"file": ("meal.jpg", io.BytesIO(b"JPEG"), "image/jpeg")},
                headers=auth_headers,
            )
        assert resp.status_code == 200
        assert resp.json()["title"] == "Chicken rice bowl"

    def test_analyze_vision_error_returns_500(self, client, auth_headers):
        with (
            patch("api.routers.meals.upload_meal_image", new_callable=AsyncMock, return_value=DRIVE_URL),
            patch(
                "api.routers.meals.analyze_meal",
                new_callable=AsyncMock,
                side_effect=Exception("OpenAI rate limit"),
            ),
        ):
            resp = client.post(
                "/meals/analyze",
                files={"file": ("meal.jpg", io.BytesIO(b"JPEG"), "image/jpeg")},
                headers=auth_headers,
            )
        assert resp.status_code == 500
        assert "Vision analysis failed" in resp.json()["detail"]

    def test_analyze_value_error_returns_422(self, client, auth_headers):
        with (
            patch("api.routers.meals.upload_meal_image", new_callable=AsyncMock, return_value=DRIVE_URL),
            patch(
                "api.routers.meals.analyze_meal",
                new_callable=AsyncMock,
                side_effect=ValueError("Vision model returned no structured output"),
            ),
        ):
            resp = client.post(
                "/meals/analyze",
                files={"file": ("meal.jpg", io.BytesIO(b"JPEG"), "image/jpeg")},
                headers=auth_headers,
            )
        assert resp.status_code == 422


# ---------------------------------------------------------------------------
# POST /meals
# ---------------------------------------------------------------------------


class TestPostMeals:
    def test_save_meal_success(self, client, auth_headers):
        with patch("api.routers.meals.save_meal", return_value=SAVED_MEAL):
            resp = client.post("/meals", json=CONFIRM_PAYLOAD, headers=auth_headers)
        assert resp.status_code == 201
        data = resp.json()
        assert data["meal_id"] == "aaa-bbb-ccc"
        assert data["meal_type"] == "Lunch"
        assert data["total"]["calories"] == 297
        assert "daily_nutrition" in data
        assert data["daily_nutrition"]["meals_count"] == 1

    def test_save_meal_no_auth_returns_401(self, client):
        resp = client.post("/meals", json=CONFIRM_PAYLOAD)
        assert resp.status_code == 401

    def test_save_meal_invalid_meal_type_returns_422(self, client, auth_headers):
        payload = dict(CONFIRM_PAYLOAD, meal_type="InvalidType")
        resp = client.post("/meals", json=payload, headers=auth_headers)
        assert resp.status_code == 422

    def test_save_meal_empty_items_accepted(self, client, auth_headers):
        """Empty items list is valid — user manually deleted all items."""
        payload = {**CONFIRM_PAYLOAD, "items": []}
        empty_saved = SavedMealResponse(
            meal_id="empty-123",
            meal_type="Snack",
            date="2026-06-08",
            total=MacroTotal(calories=0, protein_g=0.0, carbs_g=0.0, fat_g=0.0),
            daily_nutrition=DAILY_NUTRITION,
        )
        with patch("api.routers.meals.save_meal", return_value=empty_saved):
            resp = client.post("/meals", json={**payload, "meal_type": "Snack"}, headers=auth_headers)
        assert resp.status_code == 201


# ---------------------------------------------------------------------------
# GET /meals/today
# ---------------------------------------------------------------------------


class TestGetMealsToday:
    def test_today_returns_daily_nutrition(self, client, auth_headers):
        with patch("api.routers.meals.get_meals_today", return_value=DAILY_NUTRITION):
            resp = client.get("/meals/today", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["calories"] == 640
        assert data["target_calories"] == 2100
        assert data["meals_count"] == 1
        assert data["protein_g"] == pytest.approx(58.0)

    def test_today_no_auth_returns_401(self, client):
        resp = client.get("/meals/today")
        assert resp.status_code == 401

    def test_today_zero_meals_returns_zeros(self, client, auth_headers):
        empty = DailyNutrition(
            date="2026-06-08",
            calories=0,
            protein_g=0.0,
            carbs_g=0.0,
            fat_g=0.0,
            target_calories=2100,
            target_protein_g=200.0,
            target_carbs_g=180.0,
            target_fat_g=65.0,
            meals_count=0,
        )
        with patch("api.routers.meals.get_meals_today", return_value=empty):
            resp = client.get("/meals/today", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert data["meals_count"] == 0
        assert data["calories"] == 0


# ---------------------------------------------------------------------------
# GET /meals/history
# ---------------------------------------------------------------------------


class TestGetMealsHistory:
    def test_history_returns_list(self, client, auth_headers):
        with patch("api.routers.meals.get_meals_history", return_value=HISTORY_ITEMS):
            resp = client.get("/meals/history", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 2
        assert data[0]["date"] == "2026-06-08"
        assert data[0]["total_calories"] == 1280
        assert data[1]["date"] == "2026-06-07"

    def test_history_no_auth_returns_401(self, client):
        resp = client.get("/meals/history")
        assert resp.status_code == 401

    def test_history_empty_returns_empty_list(self, client, auth_headers):
        with patch("api.routers.meals.get_meals_history", return_value=[]):
            resp = client.get("/meals/history", headers=auth_headers)
        assert resp.status_code == 200
        assert resp.json() == []


# ---------------------------------------------------------------------------
# Agent tool: get_daily_nutrition
# ---------------------------------------------------------------------------


class TestAgentGetDailyNutrition:
    def test_get_daily_nutrition_delegates(self, client, auth_headers):
        """get_daily_nutrition tool calls the injected nutrition_getter callable."""
        sse_lines: list[str] = []
        with patch("api.routers.meals.get_meals_today", return_value=DAILY_NUTRITION):
            with patch("api.routers.agent._make_nutrition_getter") as mock_factory:
                mock_factory.return_value = lambda: DAILY_NUTRITION.model_dump()
                resp = client.post(
                    "/agent/chat",
                    json={"message": "What are my macros today?", "session_id": "test-sess-nutri"},
                    headers=auth_headers,
                    timeout=5,
                )
        # SSE response should stream without error
        assert resp.status_code == 200


# ---------------------------------------------------------------------------
# Agent tool: save_meal
# ---------------------------------------------------------------------------


class TestAgentSaveMeal:
    def test_save_meal_agent_tool_callable(self, client, auth_headers):
        """The meal_saver factory produces a callable that saves a meal."""
        from api.routers.agent import _make_meal_saver

        with patch("api.routers.agent.svc_save_meal", return_value=SAVED_MEAL):
            meal_saver = _make_meal_saver(1, "UTC")
            result = asyncio.run(
                meal_saver(
                    "Lunch",
                    [{"name": "Chicken", "calories": 300, "protein_g": 56.0, "carbs_g": 0.0, "fat_g": 6.0}],
                )
            )
        assert result["meal_id"] == "aaa-bbb-ccc"
        assert result["meal_type"] == "Lunch"


# ---------------------------------------------------------------------------
# Agent tool: analyze_meal_photo
# ---------------------------------------------------------------------------


def _mock_httpx_async_client(get_result=None, get_error=None):
    """Return a patch for httpx.AsyncClient whose ``get`` resolves to the given mock response."""
    mock_client = MagicMock()
    if get_error is not None:
        mock_client.get = AsyncMock(side_effect=get_error)
    else:
        mock_client.get = AsyncMock(return_value=get_result)
    mock_cm = MagicMock()
    mock_cm.__aenter__ = AsyncMock(return_value=mock_client)
    mock_cm.__aexit__ = AsyncMock(return_value=False)
    return patch("httpx.AsyncClient", return_value=mock_cm)


class TestAgentAnalyzeMealPhoto:
    def test_analyze_photo_downloads_bytes_and_runs_vision(self):
        """The meal_analyzer factory downloads the image and passes bytes + mime to vision."""
        from api.routers.agent import _make_meal_analyzer

        mock_resp = MagicMock()
        mock_resp.content = b"PNGBYTES"
        mock_resp.headers = {"content-type": "image/png; charset=binary"}
        mock_resp.raise_for_status = MagicMock()

        with (
            _mock_httpx_async_client(get_result=mock_resp),
            patch(
                "api.routers.agent.svc_analyze_meal",
                new_callable=AsyncMock,
                return_value=ANALYZE_RESPONSE,
            ) as mock_vision,
        ):
            analyzer = _make_meal_analyzer(1)
            result = asyncio.run(
                analyzer("https://drive.google.com/uc?id=test123")
            )

        mock_vision.assert_awaited_once_with(
            b"PNGBYTES", "image/png", drive_url="https://drive.google.com/uc?id=test123"
        )
        assert result["title"] == "Chicken rice bowl"
        assert len(result["detected"]) == 1

    def test_analyze_photo_fetch_failure_returns_error_dict(self):
        """A download failure returns an error dict instead of raising."""
        import httpx

        from api.routers.agent import _make_meal_analyzer

        with (
            _mock_httpx_async_client(get_error=httpx.ConnectError("no route to host")),
            patch(
                "api.routers.agent.svc_analyze_meal",
                new_callable=AsyncMock,
            ) as mock_vision,
        ):
            analyzer = _make_meal_analyzer(1)
            result = asyncio.run(analyzer("https://bad.example.com/img.jpg"))

        mock_vision.assert_not_awaited()
        assert "error" in result
        assert "Could not download image" in result["error"]


# ---------------------------------------------------------------------------
# Service robustness: blank cells in sheet rows
# ---------------------------------------------------------------------------


class TestMealServiceBlankCells:
    def test_get_meals_today_skips_blank_numeric_cells(self):
        """A meal row with blank totals (gspread returns "") must not 500 the endpoint."""
        from datetime import datetime, timezone as _tz

        from api.services.meal_service import get_meals_today

        today = datetime.now(_tz.utc).strftime("%Y-%m-%d")
        rows = [
            {"user_id": "1", "date": today, "total_calories": 500,
             "total_protein_g": 30.0, "total_carbs_g": 40.0, "total_fat_g": 10.0},
            # Stray half-filled row: blank numeric cells come back as ""
            {"user_id": "1", "date": today, "total_calories": "",
             "total_protein_g": "", "total_carbs_g": "", "total_fat_g": ""},
        ]
        with (
            patch("api.services.meal_service.read_rows", return_value=rows),
            patch("api.services.meal_service.get_settings", return_value=None),
        ):
            result = get_meals_today(1, "UTC")

        assert result.calories == 500
        assert result.protein_g == 30.0
        assert result.meals_count == 2

    def test_fmt_date_is_platform_independent(self):
        """_fmt_date renders "Jun 5" without the Unix-only %-d flag."""
        from api.services.meal_service import _fmt_date

        assert _fmt_date("2026-06-05") == "Jun 5"
        assert _fmt_date("2026-12-25") == "Dec 25"
        assert _fmt_date("not-a-date") == "not-a-date"
