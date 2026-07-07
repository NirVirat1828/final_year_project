from __future__ import annotations

from typing import List

from pydantic import BaseModel, ConfigDict, Field, StrictStr, validator
from typing import List, Optional

from app.core.config import MODEL_VERSION
from app.services.decision_engine import BusinessDecision


class _StrictBaseModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
        validate_assignment=True,
    )


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


class ModelAgreementDetail(_StrictBaseModel):
    model_name: StrictStr
    predicted_class: StrictStr
    prediction_probabilities: Optional[dict[str, float]] = Field(default=None, description="Prediction probability mapping if available")
    confidence_score: float
    inference_status: StrictStr


class ConsensusAnalysis(_StrictBaseModel):
    consensus_prediction: StrictStr
    agreement_percentage: float
    agreement_level: StrictStr
    total_discovered_models: int
    successfully_executed_models: int
    failed_models: int
    model_predictions: List[ModelAgreementDetail]


class InferenceResponse(_StrictBaseModel):
    status: StrictStr
    model_version: StrictStr = Field(default=MODEL_VERSION, description="The active version of the ML engine.")
    batch_id: StrictStr
    processing_latency_ms: float
    results: InferenceResults
    logistics: InferenceLogistics
    business_decision: Optional[BusinessDecision] = Field(default=None, description="Business-oriented recommendations from the Decision Engine")
    agreement_analysis: Optional[ConsensusAnalysis] = Field(default=None, description="Model agreement consensus analysis")



class FeatureContribution(_StrictBaseModel):
    rank: int = Field(description="The importance rank of the feature (1 is most important).")
    feature_name: StrictStr = Field(description="The original human-readable name of the feature.")
    shap_value: float = Field(description="The raw SHAP value indicating directional impact.")
    absolute_importance: float = Field(description="The absolute magnitude of the SHAP value, used for ranking.")
    impact: StrictStr = Field(description="Whether this feature increases, decreases, or has neutral impact on the prediction.")


class ModelExplanation(_StrictBaseModel):
    base_value: float = Field(default=0.0, description="The expected value (base value) of the SHAP explainer before feature contributions.")
    top_features: List[FeatureContribution] = Field(description="The top contributing features ordered by absolute importance.")


class PredictionSummary(_StrictBaseModel):
    estimated_age_days: float = Field(description="Predicted storage age of the orange in days.")
    folic_acid_uM: float = Field(description="Predicted folic acid concentration in micromolar (uM).")
    freshness_grade: StrictStr = Field(description="The assigned categorical freshness grade (e.g., A, B, C, Reject).")


class ExplanationPayload(_StrictBaseModel):
    day_model: ModelExplanation = Field(description="Explanation mapping for the storage age prediction model.")
    folic_model: ModelExplanation = Field(description="Explanation mapping for the folic acid prediction model.")


class ExplainResponse(_StrictBaseModel):
    api_version: StrictStr = Field(default="v1", description="API version of the response.")
    model_version: StrictStr = Field(default=MODEL_VERSION, description="The active version of the ML engine.")
    status: StrictStr = Field(description="Success or failure status.")
    batch_id: StrictStr = Field(description="The unique identifier for the batch of oranges.")
    processing_latency_ms: float = Field(description="Total latency in milliseconds for preprocessing, inference, and SHAP computation.")
    prediction: PredictionSummary = Field(description="The standard freshness predictions and grading.")
    explanation: ExplanationPayload = Field(description="Detailed SHAP explanations detailing feature impacts.")
