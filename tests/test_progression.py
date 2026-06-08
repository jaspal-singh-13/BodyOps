"""
Unit tests for compute_suggestion() in api/services/workout_service.py.
Pure function — no mocking or fixtures needed.
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

from api.services.workout_service import compute_suggestion


def test_first_session_returns_null_suggestion():
    s = compute_suggestion("Bench Press", 8, 12, None, None)
    assert s.weight_kg is None
    assert s.reps is None
    assert s.note == "first session"


def test_hit_upper_range_increases_weight():
    s = compute_suggestion("Bench Press", 8, 12, 60.0, 12)
    assert s.weight_kg == 62.5
    assert s.reps == 8  # reset to rep_min
    assert s.note == "increase weight"


def test_exceeds_upper_range_still_increases_weight():
    s = compute_suggestion("Bench Press", 8, 12, 60.0, 14)
    assert s.weight_kg == 62.5
    assert s.note == "increase weight"


def test_middle_of_range_adds_rep():
    # rep_mid = (8 + 12) / 2 = 10; last_reps=10 >= 10 → add rep
    s = compute_suggestion("Bench Press", 8, 12, 60.0, 10)
    assert s.weight_kg == 60.0
    assert s.reps == 11
    assert s.note == "add rep"


def test_below_middle_reduces_weight():
    # rep_mid = 10; last_reps=7 < 10 → reduce weight
    s = compute_suggestion("Bench Press", 8, 12, 60.0, 7)
    assert s.weight_kg == 57.5
    assert s.reps == 7
    assert s.note == "reduce weight"


def test_weight_floor_at_zero():
    s = compute_suggestion("Bench Press", 8, 12, 2.5, 5)
    assert s.weight_kg == 0.0


def test_single_rep_target_hit_increases_weight():
    # rep_min == rep_max == 5; rep_mid == 5.0; last_reps=5 >= 5 → increase weight
    s = compute_suggestion("Deadlift", 5, 5, 100.0, 5)
    assert s.weight_kg == 102.5
    assert s.reps == 5
    assert s.note == "increase weight"


def test_single_rep_target_miss_reduces_weight():
    s = compute_suggestion("Deadlift", 5, 5, 100.0, 4)
    assert s.weight_kg == 97.5
    assert s.note == "reduce weight"


def test_just_below_upper_range_adds_rep():
    # rep_min=8, rep_max=12, rep_mid=10; last_reps=11 >= 10 → add rep
    s = compute_suggestion("Row", 8, 12, 50.0, 11)
    assert s.note == "add rep"
    assert s.reps == 12


def test_weight_increment_rounds_correctly():
    s = compute_suggestion("Curl", 10, 15, 17.5, 15)
    assert s.weight_kg == 20.0
