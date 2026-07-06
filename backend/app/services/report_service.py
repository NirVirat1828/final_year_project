"""
Report Service Module.

Orchestrates PDF report generation by retrieving prediction records from
the database, transforming stored JSON payloads into structured Python
objects, and delegating rendering to the PDF generator utility.

All business logic for report generation lives here.  Routers should
call ``generate_prediction_report`` and never interact with the PDF
layer directly.
"""

from __future__ import annotations

import json
import time
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.logging_config import logger
from app.database.models import PredictionHistory
from app.services.history_service import get_prediction_by_id
from app.utils.pdf_generator import generate_prediction_pdf


# ──────────────────────────────────────────────────────────────────────
# Internal helpers
# ──────────────────────────────────────────────────────────────────────

def _safe_json_loads(raw: Optional[str]) -> Dict[str, Any]:
    """
    Safely deserialize a JSON string into a dictionary.

    Args:
        raw: The raw JSON string, or ``None``.

    Returns:
        The parsed dictionary, or an empty dict on failure.
    """
    if raw is None:
        return {}
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        logger.warning("Failed to parse stored JSON payload")
        return {}


def _build_record_dict(prediction: PredictionHistory) -> Dict[str, Any]:
    """
    Transform a ``PredictionHistory`` ORM object and its stored JSON
    payloads into the flat dictionary expected by ``generate_prediction_pdf``.

    Args:
        prediction: The SQLAlchemy model instance retrieved from the database.

    Returns:
        A flat dictionary containing every field the PDF generator requires.
    """
    request_data = _safe_json_loads(prediction.request_json)
    response_data = _safe_json_loads(prediction.response_json)

    results = response_data.get("results", {})
    logistics = response_data.get("logistics", {})

    # Optional SHAP explanation data
    explanation = response_data.get("explanation", {})
    if "day_model" in explanation:
        shap_features = explanation.get("day_model", {}).get("top_features", [])
    else:
        shap_features = explanation.get("top_features", [])

    return {
        # Identity
        "prediction_id": prediction.id,
        "batch_id": prediction.batch_id,
        "model_version": prediction.model_version,

        # Timing
        "created_at": prediction.created_at,
        "latency_ms": prediction.latency_ms,

        # Request fields
        "sensor_readings": request_data.get("sensor_readings", []),
        "storage_temperature": prediction.storage_temperature,
        "endpoint": "/api/v1/analyze-batch",

        # Prediction output
        "prediction_days": prediction.prediction_days,
        "estimated_age_days": logistics.get(
            "estimated_age_days", prediction.prediction_days
        ),
        "freshness_grade": prediction.freshness_grade,
        "confidence": prediction.confidence,
        "nutritional_status": results.get("nutritional_status", "N/A"),
        
        # Optional Features
        "shap_features": shap_features,
    }


# ──────────────────────────────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────────────────────────────

def generate_prediction_report(prediction_id: int, db: Session) -> Optional[bytes]:
    """
    Generate a PDF report for a specific prediction record.

    Retrieves the record from the database, deserializes the stored JSON
    payloads, assembles a structured dictionary, and delegates to the PDF
    generator.

    Args:
        prediction_id: The primary-key ID of the prediction to report on.
        db: The active SQLAlchemy database session.

    Returns:
        The PDF document as raw ``bytes``, or ``None`` if the record
        does not exist.
    """
    prediction = get_prediction_by_id(db, prediction_id=prediction_id)
    if prediction is None:
        logger.warning(f"Prediction id={prediction_id} not found for report generation")
        return None

    logger.info(
        f"PDF report requested: prediction_id={prediction_id}, "
        f"batch_id={prediction.batch_id}"
    )

    start_time = time.perf_counter()
    record = _build_record_dict(prediction)
    
    try:
        pdf_bytes = generate_prediction_pdf(record)
    except Exception as e:
        logger.error(
            f"PDF generation failed: prediction_id={prediction_id}, "
            f"batch_id={prediction.batch_id}, error={e}"
        )
        raise e
        
    latency_ms = (time.perf_counter() - start_time) * 1000
    file_size = len(pdf_bytes)

    logger.info(
        f"PDF generated successfully: prediction_id={prediction_id}, "
        f"batch_id={prediction.batch_id}, size_bytes={file_size}, "
        f"latency_ms={latency_ms:.2f}"
    )
    
    return pdf_bytes
