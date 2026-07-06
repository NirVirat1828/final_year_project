from sqlalchemy.orm import Session
from sqlalchemy import func
from app.database.models import PredictionHistory
from app.schemas.history import PredictionHistoryListResponse
from typing import Optional
import math

def save_prediction(
    db: Session,
    batch_id: str,
    request_json: str,
    response_json: str,
    prediction_days: float,
    freshness_grade: str,
    confidence: float,
    storage_temperature: float,
    model_version: str,
    latency_ms: float
) -> PredictionHistory:
    """
    Saves a new prediction record to the database.

    Args:
        db (Session): The active database session.
        batch_id (str): Identifier for the inference batch.
        request_json (str): The raw request payload in JSON format.
        response_json (str): The generated response payload in JSON format.
        prediction_days (float): The estimated age in days.
        freshness_grade (str): The calculated freshness grade.
        confidence (float): The model's confidence score.
        storage_temperature (float): The temperature parameter used during inference.
        model_version (str): The version of the ML model used.
        latency_ms (float): Request processing latency in milliseconds.

    Returns:
        PredictionHistory: The committed SQLAlchemy prediction model instance.
    """
    db_obj = PredictionHistory(
        batch_id=batch_id,
        request_json=request_json,
        response_json=response_json,
        prediction_days=prediction_days,
        freshness_grade=freshness_grade,
        confidence=confidence,
        storage_temperature=storage_temperature,
        model_version=model_version,
        latency_ms=latency_ms
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj

def get_prediction_history(db: Session, page: int = 1, page_size: int = 50) -> PredictionHistoryListResponse:
    """
    Retrieves a paginated list of stored predictions ordered chronologically (newest first).

    Args:
        db (Session): The active database session.
        page (int): The requested page number (starts at 1).
        page_size (int): The amount of records to retrieve per page.

    Returns:
        PredictionHistoryListResponse: A structured paginated response model containing the records.
    """
    offset = (page - 1) * page_size
    total_records = db.query(func.count(PredictionHistory.id)).scalar()
    total_pages = math.ceil(total_records / page_size) if total_records else 0
    predictions = db.query(PredictionHistory).order_by(PredictionHistory.created_at.desc()).offset(offset).limit(page_size).all()
    
    return PredictionHistoryListResponse(
        page=page,
        page_size=page_size,
        total_records=total_records,
        total_pages=total_pages,
        predictions=predictions
    )

def get_prediction_by_id(db: Session, prediction_id: int) -> Optional[PredictionHistory]:
    """
    Retrieves a specific prediction record by its unique database ID.

    Args:
        db (Session): The active database session.
        prediction_id (int): The ID of the record to locate.

    Returns:
        Optional[PredictionHistory]: The prediction record if found, otherwise None.
    """
    return db.query(PredictionHistory).filter(PredictionHistory.id == prediction_id).first()

def delete_prediction(db: Session, prediction_id: int) -> bool:
    """
    Deletes a specific prediction record from the database by its ID.

    Args:
        db (Session): The active database session.
        prediction_id (int): The ID of the prediction record to delete.

    Returns:
        bool: True if the record was found and deleted, False otherwise.
    """
    obj = db.query(PredictionHistory).filter(PredictionHistory.id == prediction_id).first()
    if obj:
        db.delete(obj)
        db.commit()
        return True
    return False

def get_prediction_stats(db: Session) -> dict:
    """
    Computes aggregate statistics from the PredictionHistory table.

    Args:
        db (Session): The active database session.

    Returns:
        dict: Aggregated statistics.
    """
    total = db.query(func.count(PredictionHistory.id)).scalar() or 0
    avg_confidence = db.query(func.avg(PredictionHistory.confidence)).scalar() or 0.0
    avg_latency = db.query(func.avg(PredictionHistory.latency_ms)).scalar() or 0.0
    latest = db.query(PredictionHistory).order_by(PredictionHistory.created_at.desc()).first()

    return {
        "total_predictions": total,
        "average_confidence": round(avg_confidence, 2),
        "average_latency": round(avg_latency, 2),
        "latest_prediction": {
            "id": latest.id if latest else None,
            "grade": latest.freshness_grade if latest else "N/A"
        },
        "model_version": latest.model_version if latest else "v1.0.0",
        "backend_status": "Online"
    }
