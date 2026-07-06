from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class PredictionHistoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    batch_id: str
    request_json: str
    response_json: str
    prediction_days: float
    freshness_grade: str
    confidence: float
    storage_temperature: float
    model_version: str
    latency_ms: float
    created_at: datetime


class PredictionHistoryListResponse(BaseModel):
    page: int
    page_size: int
    total_records: int
    total_pages: int
    predictions: List[PredictionHistoryResponse]
