from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, Depends, Request, HTTPException, File, UploadFile, Form
from fastapi.responses import Response

from app.core.ml_engine import OrangeFreshnessPredictor
from app.schemas.payload import InferenceRequest, InferenceResponse, ExplainResponse
from app.services.grading_service import process_batch_inference
from app.services.explain_service import process_explanation
from app.services.shap_visualization import generate_waterfall_plot, generate_bar_plot
from app.services.csv_service import process_csv_batch
from app.core.logging_config import logger
from app.core.config import MODEL_VERSION

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
    logger.info(f"Prediction request received for batch_id={request_payload.batch_id}")
    try:
        response = process_batch_inference(request_payload, ml_engine)
        logger.info(
            "Prediction completed",
            extra={
                "batch_id": request_payload.batch_id,
                "latency_ms": response.processing_latency_ms,
                "model_version": MODEL_VERSION
            }
        )
        return response
    except Exception as e:
        logger.error(f"Prediction failed for batch_id={request_payload.batch_id}: {e}")
        raise HTTPException(status_code=500, detail="Prediction generation failed")


@router.post(
    "/explain",
    response_model=ExplainResponse,
    summary="Explain Model Predictions",
    description="Returns the ML predictions along with SHAP-based feature contributions indicating why the model made these predictions.",
    responses={
        422: {"description": "Validation Error"},
        500: {"description": "Explanation generation failed"}
    },
    openapi_extra={
        "requestBody": {
            "content": {
                "application/json": {
                    "example": {
                        "batch_id": "test-batch",
                        "sensor_readings": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0],
                        "preprocessing_strategy": "raw",
                        "storage_temperature_c": 4.0
                    }
                }
            }
        }
    }
)
def explain_prediction(
    request_payload: InferenceRequest,
    ml_engine: OrangeFreshnessPredictor = Depends(get_ml_engine),
) -> ExplainResponse:
    logger.info(f"Explanation request received for batch_id={request_payload.batch_id}")
    start_time = perf_counter()
    try:
        raw_exp = process_explanation(request_payload, ml_engine)
    except Exception as e:
        logger.error(f"Explanation failed for batch_id={request_payload.batch_id}: {e}")
        raise HTTPException(status_code=500, detail="Explanation generation failed")
    
    latency = (perf_counter() - start_time) * 1000.0
    logger.info(
        "Explanation completed",
        extra={
            "batch_id": request_payload.batch_id,
            "latency_ms": latency,
            "model_version": MODEL_VERSION
        }
    )
    
    return ExplainResponse(
        status="success",
        batch_id=request_payload.batch_id,
        processing_latency_ms=latency,
        prediction=raw_exp["prediction"],
        explanation=raw_exp["explanation"]
    )


@router.post(
    "/explain/visualize",
    responses={
        200: {
            "content": {"image/png": {}}
        },
        400: {"description": "Invalid query parameters"},
        422: {"description": "Validation Error"},
        500: {"description": "Visualization generation failed"}
    },
    summary="Visualize SHAP Explanations",
    description="Returns a PNG image of a SHAP waterfall or bar plot for a given inference request."
)
def visualize_explanation(
    request_payload: InferenceRequest,
    model: str = "day",
    plot_type: str = "waterfall",
    ml_engine: OrangeFreshnessPredictor = Depends(get_ml_engine),
) -> Response:
    if model not in ["day", "folic"]:
        raise HTTPException(status_code=400, detail="model must be 'day' or 'folic'")
    if plot_type not in ["waterfall", "bar"]:
        raise HTTPException(status_code=400, detail="plot_type must be 'waterfall' or 'bar'")
        
    logger.info(f"Visualization request received: batch_id={request_payload.batch_id}, model={model}, type={plot_type}")
    
    try:
        raw_exp = process_explanation(request_payload, ml_engine)
        
        if plot_type == "waterfall":
            image_bytes = generate_waterfall_plot(raw_exp, model)
        else:
            image_bytes = generate_bar_plot(raw_exp, model)
            
        return Response(content=image_bytes, media_type="image/png")
    except Exception as e:
        logger.error(f"Visualization failed: {e}")
        raise HTTPException(status_code=500, detail="Visualization generation failed")


@router.post("/analyze-csv")
async def analyze_csv(
    request: Request,
    file: UploadFile = File(...),
    preprocessing_strategy: str = Form("raw"),
    storage_temperature_c: float = Form(4.0),
    ml_engine: OrangeFreshnessPredictor = Depends(get_ml_engine),
) -> dict:
    logger.info(f"CSV batch prediction request received for file: {file.filename}")
    try:
        file_bytes = await file.read()
        response = process_csv_batch(
            file_bytes=file_bytes,
            preprocessing_strategy=preprocessing_strategy,
            storage_temperature_c=storage_temperature_c,
            ml_engine=ml_engine,
        )
        logger.info(f"CSV batch prediction completed for file {file.filename}: {response['total_samples']} samples processed.")
        return response
    except ValueError as e:
        logger.warning(f"Validation error processing CSV: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"CSV batch prediction failed: {e}")
        raise HTTPException(status_code=500, detail="Failed to process CSV file and generate predictions")

