"""
Tests for the meal vision service (api/services/meal_vision.py).

Covers:
  - Valid structured-output response → parsed AnalyzeMealResponse
  - Empty items list (unrecognisable image) → valid empty response
  - Structured output returns None → ValueError raised
  - Confidence mapping preserved per item
  - Totals are computed from items (not trusted from model)
"""

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

import pytest

from api.models.meal import AnalyzeMealResponse, DetectedItem, MacroTotal


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_parse_result(title: str, confidence: str, items: list[dict]):
    """Build a mock structured-output parse result from raw dicts."""

    class _Item:
        def __init__(self, d: dict):
            self.name = d["name"]
            self.quantity = d.get("quantity", "100 g")
            self.calories = d.get("calories", 0)
            self.protein_g = d.get("protein_g", 0.0)
            self.carbs_g = d.get("carbs_g", 0.0)
            self.fat_g = d.get("fat_g", 0.0)
            self.confidence = d.get("confidence", "med")

    class _Parsed:
        def __init__(self):
            self.title = title
            self.overall_confidence = confidence
            self.items = [_Item(it) for it in items]

    class _Choice:
        def __init__(self):
            self.message = MagicMock(parsed=_Parsed())

    class _Completion:
        def __init__(self):
            self.choices = [_Choice()]

    return _Completion()


def _mock_client(completion):
    """Return a mock AsyncAzureOpenAI whose beta.chat.completions.parse returns the completion."""
    mock_client = MagicMock()
    mock_client.beta = MagicMock()
    mock_client.beta.chat = MagicMock()
    mock_client.beta.chat.completions = MagicMock()
    mock_client.beta.chat.completions.parse = AsyncMock(return_value=completion)
    return mock_client


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------


class TestAnalyzeMeal:
    @pytest.mark.asyncio
    async def test_valid_response_parses_correctly(self):
        """Full valid response is parsed into AnalyzeMealResponse."""
        items = [
            {"name": "Grilled chicken", "quantity": "180 g", "calories": 297, "protein_g": 56.0, "carbs_g": 0.0, "fat_g": 6.0, "confidence": "high"},
            {"name": "Jasmine rice", "quantity": "150 g", "calories": 195, "protein_g": 4.0, "carbs_g": 44.0, "fat_g": 1.0, "confidence": "high"},
        ]
        completion = _make_parse_result("Chicken rice bowl", "high", items)

        with patch("api.services.meal_vision.get_async_client", return_value=_mock_client(completion)):
            from api.services.meal_vision import analyze_meal
            result = await analyze_meal("https://drive.google.com/uc?id=abc", "https://drive.google.com/uc?id=abc")

        assert isinstance(result, AnalyzeMealResponse)
        assert result.title == "Chicken rice bowl"
        assert result.confidence == "high"
        assert len(result.detected) == 2
        assert result.detected[0].name == "Grilled chicken"
        assert result.detected[0].confidence == "high"

    @pytest.mark.asyncio
    async def test_totals_computed_from_items(self):
        """Total macros are summed from items, not trusted directly from model output."""
        items = [
            {"name": "Item A", "calories": 100, "protein_g": 10.0, "carbs_g": 5.0, "fat_g": 3.0},
            {"name": "Item B", "calories": 200, "protein_g": 20.0, "carbs_g": 15.0, "fat_g": 7.0},
        ]
        completion = _make_parse_result("Test meal", "med", items)

        with patch("api.services.meal_vision.get_async_client", return_value=_mock_client(completion)):
            from api.services.meal_vision import analyze_meal
            result = await analyze_meal("https://example.com/img.jpg", "https://example.com/img.jpg")

        assert result.total.calories == 300
        assert result.total.protein_g == pytest.approx(30.0, abs=0.1)
        assert result.total.carbs_g == pytest.approx(20.0, abs=0.1)
        assert result.total.fat_g == pytest.approx(10.0, abs=0.1)

    @pytest.mark.asyncio
    async def test_empty_items_returns_valid_response(self):
        """Empty items list (unrecognisable image) returns valid zero-total response."""
        completion = _make_parse_result("Unrecognised", "low", [])

        with patch("api.services.meal_vision.get_async_client", return_value=_mock_client(completion)):
            from api.services.meal_vision import analyze_meal
            result = await analyze_meal("https://example.com/bad.jpg", "https://example.com/bad.jpg")

        assert result.detected == []
        assert result.total.calories == 0
        assert result.confidence == "low"

    @pytest.mark.asyncio
    async def test_none_parsed_raises_value_error(self):
        """If structured output returns None, ValueError is raised."""

        class _NoneChoice:
            def __init__(self):
                self.message = MagicMock(parsed=None)

        class _NoneCompletion:
            def __init__(self):
                self.choices = [_NoneChoice()]

        mock_client = _mock_client(_NoneCompletion())

        with patch("api.services.meal_vision.get_async_client", return_value=mock_client):
            from api.services.meal_vision import analyze_meal
            with pytest.raises(ValueError, match="no structured output"):
                await analyze_meal("https://example.com/img.jpg", "https://example.com/img.jpg")

    @pytest.mark.asyncio
    async def test_drive_url_preserved(self):
        """drive_url is passed through unchanged to the response."""
        completion = _make_parse_result("Salad", "med", [
            {"name": "Lettuce", "calories": 10, "protein_g": 1.0, "carbs_g": 2.0, "fat_g": 0.0},
        ])
        drive_url = "https://drive.google.com/uc?id=xyz123"

        with patch("api.services.meal_vision.get_async_client", return_value=_mock_client(completion)):
            from api.services.meal_vision import analyze_meal
            result = await analyze_meal(drive_url, drive_url)

        assert result.drive_url == drive_url

    @pytest.mark.asyncio
    async def test_confidence_levels_mapped_per_item(self):
        """All three confidence levels are preserved per item."""
        items = [
            {"name": "Item high", "calories": 50, "protein_g": 5.0, "carbs_g": 0.0, "fat_g": 1.0, "confidence": "high"},
            {"name": "Item med", "calories": 50, "protein_g": 5.0, "carbs_g": 0.0, "fat_g": 1.0, "confidence": "med"},
            {"name": "Item low", "calories": 50, "protein_g": 5.0, "carbs_g": 0.0, "fat_g": 1.0, "confidence": "low"},
        ]
        completion = _make_parse_result("Mixed confidence", "med", items)

        with patch("api.services.meal_vision.get_async_client", return_value=_mock_client(completion)):
            from api.services.meal_vision import analyze_meal
            result = await analyze_meal("https://example.com/img.jpg", "https://example.com/img.jpg")

        levels = [it.confidence for it in result.detected]
        assert levels == ["high", "med", "low"]
