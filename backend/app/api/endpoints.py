from __future__ import annotations

from fastapi import APIRouter, Depends, Request

from app.core.ml_engine import OrangeFreshnessPredictor
from app.schemas.payload import InferenceRequest, InferenceResponse
from app.services.grading_service import process_batch_inference

router = APIRouter(prefix="/api/v1")


def get_ml_engine(request: Request) -> OrangeFreshnessPredictor:
    ml_engine = getattr(request.app.state, "ml_engine", None)
    if ml_engine is None:
        ml_engine = OrangeFreshnessPredictor()
        request.app.state.ml_engine = ml_engine
    return ml_engine


@router.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "healthy"}


@router.post("/analyze-batch", response_model=InferenceResponse)
def analyze_batch(
    request_payload: InferenceRequest,
    ml_engine: OrangeFreshnessPredictor = Depends(get_ml_engine),
) -> InferenceResponse:
    return process_batch_inference(request_payload, ml_engine)
