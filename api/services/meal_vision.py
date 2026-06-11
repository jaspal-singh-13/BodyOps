"""
AI vision service for meal photo analysis.

Sends a meal photo URL to Azure OpenAI gpt-4o vision and returns a
structured breakdown of detected food items with estimated macros.

Reuses ``get_async_client()`` from ``api/agent/llm.py`` so that the same
Azure deployment is used consistently across the app.

Required env vars (inherited from llm.py):
    AZURE_OPENAI_API_KEY
    AZURE_OPENAI_ENDPOINT
    AZURE_OPENAI_DEPLOYMENT
    AZURE_OPENAI_API_VERSION   (optional, defaults to 2024-08-01-preview)
"""

from __future__ import annotations

import os
import time
from typing import Literal

from pydantic import BaseModel

from ..agent.llm import get_async_client
from ..logger import get_logger
from ..models.meal import AnalyzeMealResponse, DetectedItem, MacroTotal

logger = get_logger("services.meal_vision")


# ---------------------------------------------------------------------------
# Internal structured-output schema (not exposed externally)
# ---------------------------------------------------------------------------


class _ItemSchema(BaseModel):
    name: str
    quantity: str
    calories: int
    protein_g: float
    carbs_g: float
    fat_g: float
    confidence: Literal["high", "med", "low"] = "med"


class _MealAnalysisSchema(BaseModel):
    title: str
    overall_confidence: Literal["high", "med", "low"]
    items: list[_ItemSchema]


# ---------------------------------------------------------------------------
# System prompt
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a nutrition analyst. Given a photo of a meal, identify every distinct
food item and estimate its macros using standard nutrition databases.

Return a JSON object with:
  • title: a concise 2–5 word label for the overall meal
  • overall_confidence: "high" | "med" | "low" based on how clearly visible the food is
  • items: array of detected food items, each with:
      – name:       human-readable food name
      – quantity:   estimated serving size as a string (e.g. "180 g", "~1 tbsp", "1 medium")
      – calories:   estimated kcal (integer)
      – protein_g:  estimated protein in grams (float, 1 decimal)
      – carbs_g:    estimated carbohydrates in grams (float, 1 decimal)
      – fat_g:      estimated fat in grams (float, 1 decimal)
      – confidence: "high" | "med" | "low" per item
        - high: item is clearly visible and portion is obvious
        - med:  item is identifiable but portion is estimated
        - low:  item is partially visible, obscured, or a common condiment/oil

Rules:
  • Include cooking oils, dressings, or sauces if they are visibly present or
    implied by the cooking method (mark them as "low" confidence).
  • Do not invent items. If you cannot identify a food, omit it.
  • Calorie and macro values must be internally consistent
    (calories ≈ protein_g×4 + carbs_g×4 + fat_g×9).
  • If the image contains no food or is unrecognisable, return an empty items
    list with overall_confidence "low" and title "Unrecognised".
"""


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


async def analyze_meal(image_url: str, drive_url: str) -> AnalyzeMealResponse:
    """
    Analyse a meal photo and return a structured macro breakdown.

    Sends the image URL to Azure OpenAI gpt-4o vision using the SDK's
    structured-output API (``beta.chat.completions.parse``) so that the
    response is guaranteed to conform to ``_MealAnalysisSchema`` before any
    further processing.

    Args:
        image_url: Publicly accessible URL for the meal photo.  This must be
            reachable by the OpenAI API servers — a Google Drive ``uc?id=``
            URL works after the file permission is set to public reader.
        drive_url: The same (or equivalent) Drive URL stored in the response
            so the caller can pass it straight through to ``ConfirmMealRequest``
            without re-uploading.

    Returns:
        ``AnalyzeMealResponse`` with detected items, totals, and drive URL.

    Raises:
        ValueError: If the model returns an empty or unparseable response.
        openai.APIError: On OpenAI / Azure API failure.
    """
    deployment = os.environ.get("AZURE_OPENAI_DEPLOYMENT", "?")
    logger.info("Vision analysis start deployment=%s url=%s", deployment, image_url)
    t0 = time.perf_counter()

    client = get_async_client()

    completion = await client.beta.chat.completions.parse(
        model=os.environ["AZURE_OPENAI_DEPLOYMENT"],
        response_format=_MealAnalysisSchema,
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url, "detail": "high"},
                    },
                    {
                        "type": "text",
                        "text": "Analyse this meal and return the structured nutrition breakdown.",
                    },
                ],
            },
        ],
        max_tokens=1024,
    )

    elapsed_ms = (time.perf_counter() - t0) * 1000
    parsed = completion.choices[0].message.parsed
    if parsed is None:
        logger.warning(
            "Vision model returned no structured output deployment=%s url=%s (%.0f ms)",
            deployment,
            image_url,
            elapsed_ms,
        )
        raise ValueError(
            "Vision model returned no structured output — image may be unprocessable."
        )

    detected = [
        DetectedItem(
            name=it.name,
            quantity=it.quantity,
            calories=it.calories,
            protein_g=it.protein_g,
            carbs_g=it.carbs_g,
            fat_g=it.fat_g,
            confidence=it.confidence,
        )
        for it in parsed.items
    ]

    total = MacroTotal(
        calories=sum(it.calories for it in detected),
        protein_g=round(sum(it.protein_g for it in detected), 1),
        carbs_g=round(sum(it.carbs_g for it in detected), 1),
        fat_g=round(sum(it.fat_g for it in detected), 1),
    )

    logger.info(
        "Vision analysis done deployment=%s items=%d confidence=%s total_cal=%d (%.0f ms)",
        deployment,
        len(detected),
        parsed.overall_confidence,
        total.calories,
        elapsed_ms,
    )

    return AnalyzeMealResponse(
        title=parsed.title,
        confidence=parsed.overall_confidence,
        detected=detected,
        total=total,
        drive_url=drive_url,
    )
