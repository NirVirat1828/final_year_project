from sqlalchemy import Column, Integer, String, Float, DateTime
from datetime import datetime, timezone
from app.database.database import Base

class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    batch_id = Column(String, index=True)
    request_json = Column(String)
    response_json = Column(String)
    prediction_days = Column(Float)
    freshness_grade = Column(String)
    confidence = Column(Float)
    storage_temperature = Column(Float)
    model_version = Column(String)
    latency_ms = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
