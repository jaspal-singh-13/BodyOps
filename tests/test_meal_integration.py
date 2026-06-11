"""
Integration tests for the meal photo analysis pipeline.

These tests use the real kurkure.jpg image and hit the actual Azure OpenAI
and Google Drive APIs.  They are skipped automatically when the required
environment variables are not set (CI / unit-test runs).

Run locally with real credentials:
    pytest tests/test_meal_integration.py -v -s

Required env vars (from .env or shell):
    AZURE_OPENAI_API_KEY
    AZURE_OPENAI_ENDPOINT
    AZURE_OPENAI_DEPLOYMENT
    GOOGLE_SERVICE_ACCOUNT_JSON
    GOOGLE_DRIVE_FOLDER_ID
    JWT_SECRET
    GOOGLE_SPREADSHEET_ID
    GOOGLE_AUTH_SHEET_ID
"""

from __future__ import annotations

import io
import json
import os
import pathlib

import pytest

# ---------------------------------------------------------------------------
# Load .env so real credentials are available when running locally.
# Must happen before any api.* import (conftest uses setdefault so these
# real values win if they're already set by the time setdefault runs).
# ---------------------------------------------------------------------------

_ENV_PATH = pathlib.Path(__file__).parent.parent / ".env"
if _ENV_PATH.exists():
    for _line in _ENV_PATH.read_text().splitlines():
        _line = _line.strip()
        if _line and not _line.startswith("#") and "=" in _line:
            _k, _, _v = _line.partition("=")
            os.environ.setdefault(_k.strip(), _v.strip())


def _has_real_openai() -> bool:
    key = os.environ.get("AZURE_OPENAI_API_KEY", "")
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT", "")
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "")
    return bool(key and key != "test-key" and endpoint and "test" not in endpoint and deployment)


def _has_real_drive() -> bool:
    sa_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "{}")
    folder = os.environ.get("GOOGLE_DRIVE_FOLDER_ID", "")
    try:
        sa = json.loads(sa_json)
        return bool(folder and folder != "test-folder-id" and sa.get("client_email"))
    except Exception:
        return False


REQUIRED_OPENAI = pytest.mark.skipif(
    not _has_real_openai(),
    reason="Real Azure OpenAI credentials not found — skipping integration test",
)

REQUIRED_DRIVE = pytest.mark.skipif(
    not _has_real_drive(),
    reason="Real Google Drive credentials not found — skipping Drive integration test",
)

# ---------------------------------------------------------------------------
# Fixture: kurkure.jpg bytes
# ---------------------------------------------------------------------------

KURKURE_PATH = pathlib.Path(__file__).parent.parent / "kurkure.jpg"


@pytest.fixture(scope="module")
def kurkure_bytes() -> bytes:
    if not KURKURE_PATH.exists():
        pytest.skip(f"kurkure.jpg not found at {KURKURE_PATH}")
    return KURKURE_PATH.read_bytes()


# ---------------------------------------------------------------------------
# Vision service integration
# ---------------------------------------------------------------------------


class TestMealVisionIntegration:
    @REQUIRED_OPENAI
    @pytest.mark.asyncio
    async def test_analyze_kurkure_returns_snack_items(self, kurkure_bytes):
        """
        Real OpenAI call: kurkure.jpg should be identified as a snack/chips.
        Asserts the response structure is valid; exact item names may vary.
        """
        from api.services.meal_vision import analyze_meal

        result = await analyze_meal(kurkure_bytes, "image/jpeg")

        assert result.title, "title should be non-empty"
        assert result.confidence in ("high", "med", "low")
        assert isinstance(result.detected, list)
        assert len(result.detected) > 0, "should detect at least one food item"

        for item in result.detected:
            assert item.name, "each item must have a name"
            assert item.calories >= 0
            assert item.protein_g >= 0
            assert item.carbs_g >= 0
            assert item.fat_g >= 0
            assert item.confidence in ("high", "med", "low")

        # Kurkure is a snack — expect non-trivial calories
        assert result.total.calories > 0, "total calories should be > 0 for a snack"

    @REQUIRED_OPENAI
    @pytest.mark.asyncio
    async def test_analyze_kurkure_totals_match_items(self, kurkure_bytes):
        """
        Totals are computed by summing items — verify they match within rounding.
        """
        from api.services.meal_vision import analyze_meal

        result = await analyze_meal(kurkure_bytes, "image/jpeg")

        expected_cal = sum(it.calories for it in result.detected)
        expected_protein = round(sum(it.protein_g for it in result.detected), 1)
        expected_carbs = round(sum(it.carbs_g for it in result.detected), 1)
        expected_fat = round(sum(it.fat_g for it in result.detected), 1)

        assert result.total.calories == expected_cal
        assert result.total.protein_g == pytest.approx(expected_protein, abs=0.2)
        assert result.total.carbs_g == pytest.approx(expected_carbs, abs=0.2)
        assert result.total.fat_g == pytest.approx(expected_fat, abs=0.2)

    @REQUIRED_OPENAI
    @pytest.mark.asyncio
    async def test_analyze_kurkure_drive_url_passed_through(self, kurkure_bytes):
        """drive_url arg is stored on result even when Drive upload is skipped."""
        from api.services.meal_vision import analyze_meal

        fake_url = "https://drive.google.com/uc?id=test-kurkure"
        result = await analyze_meal(kurkure_bytes, "image/jpeg", drive_url=fake_url)

        assert result.drive_url == fake_url


# ---------------------------------------------------------------------------
# Router integration — full HTTP stack with real OpenAI
# ---------------------------------------------------------------------------


class TestMealRouterIntegration:
    @REQUIRED_OPENAI
    def test_post_analyze_kurkure_via_http(self, client, auth_headers, kurkure_bytes):
        """
        POST /meals/analyze with the real kurkure.jpg through the FastAPI test
        client.  Drive upload is mocked so the test only exercises OpenAI.
        """
        from unittest.mock import AsyncMock, patch

        fake_drive_url = "https://drive.google.com/uc?id=kurkure-test"

        with patch(
            "api.routers.meals.upload_meal_image",
            new_callable=AsyncMock,
            return_value=fake_drive_url,
        ):
            resp = client.post(
                "/meals/analyze",
                files={"file": ("kurkure.jpg", io.BytesIO(kurkure_bytes), "image/jpeg")},
                headers=auth_headers,
            )

        assert resp.status_code == 200, f"Unexpected error: {resp.text}"
        data = resp.json()

        assert data["title"], "title must be non-empty"
        assert data["confidence"] in ("high", "med", "low")
        assert isinstance(data["detected"], list)
        assert len(data["detected"]) > 0, "should detect at least one item"
        assert "total" in data
        assert data["total"]["calories"] > 0
        assert data["drive_url"] == fake_drive_url

    @REQUIRED_OPENAI
    @REQUIRED_DRIVE
    def test_post_analyze_kurkure_full_pipeline(self, client, auth_headers, kurkure_bytes):
        """
        Full end-to-end: real OpenAI vision + real Google Drive upload.
        Only runs when both AZURE_OPENAI_* and GOOGLE_DRIVE_* vars are set.
        """
        resp = client.post(
            "/meals/analyze",
            files={"file": ("kurkure.jpg", io.BytesIO(kurkure_bytes), "image/jpeg")},
            headers=auth_headers,
        )

        assert resp.status_code == 200, f"Full pipeline error: {resp.text}"
        data = resp.json()

        assert data["title"]
        assert len(data["detected"]) > 0
        assert data["total"]["calories"] > 0
        # Drive URL should be populated when Drive upload succeeds
        assert data["drive_url"].startswith("https://drive.google.com/")

    def test_post_analyze_wrong_mime_returns_400(self, client, auth_headers):
        """Non-image MIME type is rejected before any API call."""
        resp = client.post(
            "/meals/analyze",
            files={"file": ("doc.pdf", io.BytesIO(b"%PDF-1.4"), "application/pdf")},
            headers=auth_headers,
        )
        assert resp.status_code == 400
        assert "Unsupported image type" in resp.json()["detail"]

    def test_post_analyze_empty_file_returns_400(self, client, auth_headers):
        """Empty file body is rejected before any API call."""
        from unittest.mock import AsyncMock, patch

        with patch("api.routers.meals.upload_meal_image", new_callable=AsyncMock):
            resp = client.post(
                "/meals/analyze",
                files={"file": ("empty.jpg", io.BytesIO(b""), "image/jpeg")},
                headers=auth_headers,
            )
        assert resp.status_code == 400
        assert "empty" in resp.json()["detail"].lower()

    def test_post_analyze_no_auth_returns_401(self, client):
        """Unauthenticated request is rejected before any processing."""
        resp = client.post(
            "/meals/analyze",
            files={"file": ("meal.jpg", io.BytesIO(b"JPEG"), "image/jpeg")},
        )
        assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Drive service integration
# ---------------------------------------------------------------------------


class TestDriveServiceIntegration:
    @REQUIRED_DRIVE
    @pytest.mark.asyncio
    async def test_upload_kurkure_to_shared_drive(self, kurkure_bytes):
        """
        Real Drive upload: kurkure.jpg should be uploaded to the Shared Drive
        folder and return a public https://drive.google.com/uc?id=… URL.
        """
        from api.services.drive_service import upload_meal_image

        url = await upload_meal_image(kurkure_bytes, "image/jpeg")

        assert url.startswith("https://drive.google.com/uc?id="), (
            f"Expected a Drive uc URL, got: {url}"
        )
        file_id = url.split("id=")[-1]
        assert len(file_id) > 10, "file ID looks too short"
