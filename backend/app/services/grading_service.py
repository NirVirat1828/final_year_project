from __future__ import annotations

from time import perf_counter
from typing import Any, Dict, Tuple

import numpy as np

from app.core.ml_engine import OrangeFreshnessPredictor
from app.schemas.payload import (
    ConfidenceInterval,
    InferenceLogistics,
    InferenceRequest,
    InferenceResponse,
    InferenceResults,
)

MAX_STORAGE_DAYS = 14.0
REFERENCE_TEMP_C = 4.0
Q10 = 2.0

GRADE_DESCRIPTIONS: Dict[str, str] = {
    "A": "Premium freshness; best for immediate consumption.",
    "B": "Good quality; still suitable for short-term storage.",
    "C": "Fair quality; monitor closely before use.",
    "D": "Poor quality; consider discarding or urgent use.",
}

NUTRITIONAL_STATUS_LABELS: Tuple[Tuple[float, str], ...] = (
    (150.0, "High Value"),
    (80.0, "Acceptable"),
    (40.0, "Declining"),
)


def _grade_from_days(predicted_days: float) -> str:
    if predicted_days <= 3:
        return "A"
    if predicted_days <= 7:
        return "B"
    if predicted_days <= 10:
        return "C"
    return "D"


def _nutritional_status_from_folic(folic_acid_uM: float) -> str:
    if folic_acid_uM > 150.0:
        return "High Value"
    if folic_acid_uM >= 80.0:
        return "Acceptable"
    if folic_acid_uM >= 40.0:
        return "Declining"
    return "Depleted"


def _temperature_adjusted_remaining_shelf_life(
    predicted_days: float,
    storage_temperature_c: float,
) -> float:
    base_remaining = max(0.0, MAX_STORAGE_DAYS - predicted_days)
    temp_factor = Q10 ** ((storage_temperature_c - REFERENCE_TEMP_C) / 10.0)
    adjusted_remaining = base_remaining / temp_factor
    return max(0.0, adjusted_remaining)


def _confidence_interval(remaining_shelf_life_days: float, storage_temperature_c: float) -> ConfidenceInterval:
    temp_factor = Q10 ** ((storage_temperature_c - REFERENCE_TEMP_C) / 10.0)
    relative_margin = 0.15 * temp_factor
    absolute_margin = max(0.75, remaining_shelf_life_days * relative_margin)

    lower_bound = max(0.0, remaining_shelf_life_days - absolute_margin)
    upper_bound = remaining_shelf_life_days + absolute_margin

    return ConfidenceInterval(lower_bound=lower_bound, upper_bound=upper_bound)


def process_batch_inference(
    request: InferenceRequest,
    ml_engine: OrangeFreshnessPredictor,
) -> InferenceResponse:
    start_time = perf_counter()

    sensor_features = np.asarray(request.sensor_readings, dtype=np.float32).reshape(1, -1)
    predictions = ml_engine.predict_both(sensor_features)

    predicted_days = float(np.asarray(predictions["days"]).reshape(-1)[0])
    folic_acid_uM = float(np.asarray(predictions["folic_acid_uM"]).reshape(-1)[0])

    freshness_grade = _grade_from_days(predicted_days)
    grade_description = GRADE_DESCRIPTIONS[freshness_grade]
    nutritional_status = _nutritional_status_from_folic(folic_acid_uM)
    remaining_shelf_life_days = _temperature_adjusted_remaining_shelf_life(
        predicted_days=predicted_days,
        storage_temperature_c=request.storage_temperature_c,
    )

    response = InferenceResponse(
        status="success",
        batch_id=request.batch_id,
        processing_latency_ms=(perf_counter() - start_time) * 1000.0,
        results=InferenceResults(
            freshness_grade=freshness_grade,
            grade_description=grade_description,
            folic_acid_uM=folic_acid_uM,
            nutritional_status=nutritional_status,
        ),
        logistics=InferenceLogistics(
            estimated_age_days=predicted_days,
            remaining_shelf_life_days=remaining_shelf_life_days,
            confidence_interval=_confidence_interval(
                remaining_shelf_life_days=remaining_shelf_life_days,
                storage_temperature_c=request.storage_temperature_c,
            ),
            temperature_warning=(
                "Temperature above refrigerated baseline may accelerate spoilage."
                if request.storage_temperature_c > REFERENCE_TEMP_C
                else "Temperature within refrigerated baseline range."
            ),
        ),
    )

    return response
