from __future__ import annotations

from typing import List

from pydantic import BaseModel, Field, StrictStr, validator


class _StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"
        anystr_strip_whitespace = True
        validate_assignment = True


class InferenceRequest(_StrictBaseModel):
    batch_id: StrictStr
    sensor_readings: List[float]
    preprocessing_strategy: StrictStr = Field(default="raw")
    storage_temperature_c: float = Field(default=4.0)

    @validator("batch_id")
    def _batch_id_must_not_be_empty(cls, value: str) -> str:
        if not value:
            raise ValueError("batch_id must not be empty")
        return value

    @validator("sensor_readings")
    def _sensor_readings_must_be_exactly_11_values(cls, value: list[float]) -> list[float]:
        if len(value) != 11:
            raise ValueError("sensor_readings must contain exactly 11 floats")
        for reading in value:
            if not isinstance(reading, float):
                raise TypeError("each sensor reading must be a float")
        return value


class ConfidenceInterval(_StrictBaseModel):
    lower_bound: float
    upper_bound: float


class InferenceResults(_StrictBaseModel):
    freshness_grade: StrictStr
    grade_description: StrictStr
    folic_acid_uM: float
    nutritional_status: StrictStr


class InferenceLogistics(_StrictBaseModel):
    estimated_age_days: float
    remaining_shelf_life_days: float
    confidence_score_percent: float
    confidence_interval: ConfidenceInterval
    temperature_warning: StrictStr


class InferenceResponse(_StrictBaseModel):
    status: StrictStr
    batch_id: StrictStr
    processing_latency_ms: float
    results: InferenceResults
    logistics: InferenceLogistics
