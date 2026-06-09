from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from app.services.grading_service import (  # noqa: E402
    _grade_from_days,
    _nutritional_status_from_folic,
    _temperature_adjusted_remaining_shelf_life,
)


def test_grade_mapping() -> None:
    assert _grade_from_days(2) == "A"
    assert _grade_from_days(5) == "B"
    assert _grade_from_days(9) == "C"
    assert _grade_from_days(12) == "D"


def test_nutritional_status_mapping() -> None:
    assert _nutritional_status_from_folic(160) == "High Value"
    assert _nutritional_status_from_folic(100) == "Acceptable"
    assert _nutritional_status_from_folic(60) == "Declining"
    assert _nutritional_status_from_folic(20) == "Depleted"


def test_temperature_adjusted_shelf_life() -> None:
    adjusted_shelf_life = _temperature_adjusted_remaining_shelf_life(
        predicted_days=4.0,
        storage_temperature_c=14.0,
    )

    assert adjusted_shelf_life == pytest.approx(5.0, rel=1e-6)
