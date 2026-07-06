from __future__ import annotations

from time import perf_counter

from fastapi import APIRouter, Depends, Request, HTTPException, File, UploadFile, Form, WebSocket, WebSocketDisconnect, Query
from fastapi.responses import Response
import numpy as np

from app.core.ml_engine import OrangeFreshnessPredictor
from app.schemas.payload import InferenceRequest, InferenceResponse, ExplainResponse
from app.services.grading_service import (
    process_batch_inference,
    _grade_from_days,
    _nutritional_status_from_folic,
    _temperature_adjusted_remaining_shelf_life,
    _confidence_interval,
    GRADE_DESCRIPTIONS,
    REFERENCE_TEMP_C,
)
from app.services.explain_service import process_explanation
from app.services.shap_visualization import generate_waterfall_plot, generate_bar_plot
from app.services.csv_service import process_csv_batch, CSVPreprocessor, EXPECTED_FEATURE_COLS
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


from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.database.database import get_db
from app.services.history_service import (
    save_prediction,
    get_prediction_history,
    get_prediction_by_id,
    delete_prediction,
)
from app.services.report_service import generate_prediction_report
from app.schemas.history import PredictionHistoryResponse, PredictionHistoryListResponse

@router.post("/analyze-batch", response_model=InferenceResponse)
def analyze_batch(
    request_payload: InferenceRequest,
    ml_engine: OrangeFreshnessPredictor = Depends(get_ml_engine),
    db: Session = Depends(get_db),
) -> InferenceResponse:
    logger.info(f"Prediction request received for batch_id={request_payload.batch_id}")
    try:
        response = process_batch_inference(request_payload, ml_engine)
        
        try:
            record = save_prediction(
                db=db,
                batch_id=request_payload.batch_id,
                request_json=request_payload.model_dump_json(),
                response_json=response.model_dump_json(),
                prediction_days=response.logistics.estimated_age_days,
                freshness_grade=response.results.freshness_grade,
                confidence=response.logistics.confidence_score_percent,
                storage_temperature=request_payload.storage_temperature_c,
                model_version=MODEL_VERSION,
                latency_ms=response.processing_latency_ms
            )
            logger.info("Prediction Saved", extra={
                "batch_id": request_payload.batch_id,
                "record_id": record.id,
                "latency": response.processing_latency_ms,
                "model_version": MODEL_VERSION
            })
        except SQLAlchemyError as db_err:
            logger.error(f"Database save failed for batch_id={request_payload.batch_id}: {db_err}")

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


def get_websocket_ml_engine(websocket: WebSocket) -> OrangeFreshnessPredictor:
    ml_engine = getattr(websocket.app.state, "ml_engine", None)
    if ml_engine is None:
        ml_engine = OrangeFreshnessPredictor()
        websocket.app.state.ml_engine = ml_engine
    return ml_engine


@router.websocket("/ws/live-predict")
async def websocket_live_predict(
    websocket: WebSocket,
    ml_engine: OrangeFreshnessPredictor = Depends(get_websocket_ml_engine),
):
    await websocket.accept()
    logger.info("WebSocket connection accepted for live predictions")
    try:
        while True:
            # Receive frame: {"readings": [float, ...], "preprocessing_strategy": "raw", "storage_temperature_c": 4.0}
            data = await websocket.receive_json()
            readings = data.get("readings")
            preprocessing_strategy = data.get("preprocessing_strategy", "raw")
            storage_temperature_c = data.get("storage_temperature_c", 4.0)

            if not readings:
                await websocket.send_json({"status": "error", "message": "Missing sensor readings in frame"})
                continue

            # Process readings
            if len(readings) >= 15:
                # Raw signal
                preprocessor = CSVPreprocessor()
                signal = np.array(readings[:15], dtype=float)
                feats = preprocessor.extract_features(signal)
                sensor_features = [feats[col] for col in EXPECTED_FEATURE_COLS]
            elif len(readings) == 11:
                # Engineered features
                sensor_features = readings
            else:
                await websocket.send_json({
                    "status": "error",
                    "message": f"Invalid readings length. Expected 11 features or 15 currents. Got {len(readings)}."
                })
                continue

            # Perform prediction
            predicted_days, folic_acid_uM = ml_engine.predict_both(sensor_features)

            freshness_grade = _grade_from_days(predicted_days)
            grade_description = GRADE_DESCRIPTIONS[freshness_grade]
            nutritional_status = _nutritional_status_from_folic(folic_acid_uM)
            remaining_shelf_life_days = _temperature_adjusted_remaining_shelf_life(
                predicted_days=predicted_days,
                storage_temperature_c=storage_temperature_c,
            )

            if preprocessing_strategy.strip().lower() == "advanced":
                remaining_shelf_life_days += 2.5

            ci = _confidence_interval(
                remaining_shelf_life_days=remaining_shelf_life_days,
                storage_temperature_c=storage_temperature_c,
            )

            temperature_warning = (
                "Temperature above refrigerated baseline may accelerate spoilage."
                if storage_temperature_c > REFERENCE_TEMP_C
                else "Temperature within refrigerated baseline range."
            )

            # Send response back
            await websocket.send_json({
                "status": "success",
                "results": {
                    "freshness_grade": freshness_grade,
                    "grade_description": grade_description,
                    "folic_acid_uM": float(folic_acid_uM),
                    "nutritional_status": nutritional_status,
                },
                "logistics": {
                    "estimated_age_days": float(predicted_days),
                    "remaining_shelf_life_days": float(remaining_shelf_life_days),
                    "confidence_score_percent": 80.0 if preprocessing_strategy == "advanced" else 100.0,
                    "confidence_interval": {
                        "lower_bound": float(ci.lower_bound),
                        "upper_bound": float(ci.upper_bound),
                    },
                    "temperature_warning": temperature_warning,
                }
            })
    except WebSocketDisconnect:
        logger.info("WebSocket connection closed by client")
    except Exception as e:
        logger.error(f"WebSocket error in live predict: {e}")
        try:
            await websocket.send_json({"status": "error", "message": "Internal prediction processing error"})
        except Exception:
            pass


@router.get(
    "/history",
    response_model=PredictionHistoryListResponse,
    summary="Get Prediction History",
    description="Retrieves a paginated list of all stored predictions, ordered newest first.",
    responses={
        200: {"description": "Successfully retrieved prediction history"},
        422: {"description": "Invalid page or page_size query parameters"},
        503: {"description": "Database unavailable"}
    }
)
def get_history(
    page: int = Query(1, ge=1, description="Page number (must be >= 1)"),
    page_size: int = Query(50, ge=1, le=100, description="Number of records per page (max 100)"),
    db: Session = Depends(get_db)
):
    logger.info("History requested", extra={"page": page, "page_size": page_size})
    try:
        return get_prediction_history(db, page=page, page_size=page_size)
    except SQLAlchemyError as db_err:
        logger.error(f"Database error during history retrieval: {db_err}")
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.get(
    "/history/{id}",
    response_model=PredictionHistoryResponse,
    summary="Get Prediction by ID",
    description="Retrieves a complete stored prediction record by its unique database ID.",
    responses={
        200: {"description": "Successfully retrieved the prediction record"},
        404: {"description": "Prediction record not found or invalid history ID"},
        503: {"description": "Database unavailable"}
    }
)
def get_history_by_id(id: int, db: Session = Depends(get_db)):
    try:
        prediction = get_prediction_by_id(db, prediction_id=id)
        if not prediction:
            raise HTTPException(status_code=404, detail="Prediction not found")
        return prediction
    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.error(f"Database error retrieving prediction {id}: {db_err}")
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.delete(
    "/history/{id}",
    status_code=204,
    summary="Delete Prediction",
    description="Deletes a specific prediction record from the database by its ID.",
    responses={
        204: {"description": "Prediction successfully deleted"},
        404: {"description": "Prediction record not found or invalid history ID"},
        503: {"description": "Database unavailable"}
    }
)
def delete_history(id: int, db: Session = Depends(get_db)):
    try:
        success = delete_prediction(db, prediction_id=id)
        if not success:
            raise HTTPException(status_code=404, detail="Prediction not found")
        return Response(status_code=204)
    except HTTPException:
        raise
    except SQLAlchemyError as db_err:
        logger.error(f"Database error deleting prediction {id}: {db_err}")
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.get(
    "/history/{id}/report",
    summary="Download Prediction Report",
    description="Generates and returns a PDF report for a specific stored prediction record.",
    responses={
        200: {
            "content": {"application/pdf": {}},
            "description": "Returns the generated PDF report"
        },
        404: {"description": "Prediction record not found"},
        500: {"description": "Report generation failed"}
    }
)
def download_prediction_report(id: int, db: Session = Depends(get_db)):
    try:
        pdf_bytes = generate_prediction_report(prediction_id=id, db=db)
        if pdf_bytes is None:
            raise HTTPException(status_code=404, detail="Prediction not found")
            
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=prediction_report_{id}.pdf"}
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating report for prediction {id}: {e}")
        raise HTTPException(status_code=500, detail="Report generation failed")
