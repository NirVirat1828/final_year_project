from __future__ import annotations

import os
import time
import joblib
from pathlib import Path
from typing import Dict, Any, List, Optional
import numpy as np
from collections import Counter

from app.core.logging_config import logger
from app.core.ml_engine import _resolve_models_dir
from app.schemas.payload import ConsensusAnalysis, ModelAgreementDetail

# Global cache for loaded classification models
_CLASSIFICATION_MODELS: Dict[str, Any] = {}
_MODELS_LOADED = False


def get_or_discover_classification_models() -> Dict[str, Any]:
    """
    Dynamically discovers and loads all compatible trained classification models
    from the models directory. Cached to avoid reloading on subsequent requests.
    
    A model is considered compatible if:
    1. It is a classification model (i.e. has `_estimator_type == "classifier"`).
    2. It expects 5 input features (matching the preprocessed features shape).
    """
    global _CLASSIFICATION_MODELS, _MODELS_LOADED
    if _MODELS_LOADED:
        return _CLASSIFICATION_MODELS

    try:
        models_dir = _resolve_models_dir()
        logger.info(f"Agreement Engine: Discovering compatible classifiers in {models_dir}")
        
        if not models_dir.exists():
            logger.warning(f"Agreement Engine: Models directory {models_dir} does not exist.")
            _MODELS_LOADED = True
            return _CLASSIFICATION_MODELS

        from sklearn.base import is_classifier

        for file_path in models_dir.glob("*.pkl"):
            if file_path.name in ["scaler.pkl", "selected_features.pkl"]:
                continue
                
            try:
                model = joblib.load(file_path)
                
                # Verify that it is a classifier
                is_clf = False
                if hasattr(model, "__sklearn_tags__"):
                    is_clf = is_classifier(model)
                else:
                    is_clf = getattr(model, "_estimator_type", None) == "classifier"

                if not is_clf:
                    logger.debug(f"Agreement Engine: Skipped non-classifier model {file_path.name}")
                    continue
                
                # Check feature count compatibility (expects 5 features)
                n_features = getattr(model, "n_features_in_", None)
                if n_features != 5:
                    logger.warning(
                        f"Agreement Engine: Model {file_path.name} expects {n_features} features, "
                        f"but preprocessed feature vector has 5 features. Skipped."
                    )
                    continue
                
                model_name = file_path.stem
                _CLASSIFICATION_MODELS[model_name] = model
                logger.info(f"Agreement Engine: Loaded and registered classifier '{model_name}'")
                
            except Exception as e:
                logger.error(f"Agreement Engine: Failed to load or validate model file {file_path.name}: {e}")
                
        _MODELS_LOADED = True
    except Exception as e:
        logger.error(f"Agreement Engine: Error during model discovery: {e}")
        
    return _CLASSIFICATION_MODELS


def analyze_model_agreement(X_selected: np.ndarray) -> Optional[ConsensusAnalysis]:
    """
    Executes inference using all discovered classification models on the preprocessed
    features, calculates consensus statistics, and returns the reliability analysis.
    
    Args:
        X_selected (np.ndarray): Preprocessed, scaled, and selected 2D feature matrix (1 x 5).
        
    Returns:
        Optional[ConsensusAnalysis]: Structured agreement statistics, or None if no models are available.
    """
    start_time = time.perf_counter()
    models = get_or_discover_classification_models()
    
    total_models = len(models)
    if total_models == 0:
        logger.warning("Agreement Engine: No compatible classification models discovered.")
        return None
        
    model_predictions: List[ModelAgreementDetail] = []
    successful_preds: List[str] = []
    failed_count = 0
    skipped_count = 0
    
    for model_name, model in models.items():
        try:
            # Perform prediction
            pred_arr = model.predict(X_selected)
            pred_class = str(pred_arr[0])
            
            # Retrieve probabilities if available
            pred_proba = None
            confidence = 1.0
            if hasattr(model, "predict_proba"):
                try:
                    proba_arr = model.predict_proba(X_selected)[0]
                    # Map class label strings to floats
                    pred_proba = {str(cls): float(p) for cls, p in zip(model.classes_, proba_arr)}
                    confidence = float(np.max(proba_arr))
                except Exception as proba_err:
                    logger.warning(f"Agreement Engine: Failed to compute predict_proba for model {model_name}: {proba_err}")
            
            model_predictions.append(
                ModelAgreementDetail(
                    model_name=model_name,
                    predicted_class=pred_class,
                    prediction_probabilities=pred_proba,
                    confidence_score=confidence,
                    inference_status="success"
                )
            )
            successful_preds.append(pred_class)
            
        except Exception as e:
            logger.error(f"Agreement Engine: Inference failed for model {model_name}: {e}")
            failed_count += 1
            model_predictions.append(
                ModelAgreementDetail(
                    model_name=model_name,
                    predicted_class="N/A",
                    prediction_probabilities=None,
                    confidence_score=0.0,
                    inference_status="failed"
                )
            )

    successful_count = len(successful_preds)
    if successful_count == 0:
        logger.error("Agreement Engine: All discovered classification models failed execution.")
        return None
        
    # Calculate consensus details
    pred_counts = Counter(successful_preds)
    consensus_pred, consensus_count = pred_counts.most_common(1)[0]
    
    agreement_percentage = (consensus_count / successful_count) * 100.0
    
    # Classify agreement level
    if agreement_percentage == 100.0:
        agreement_level = "Very Strong"
    elif agreement_percentage >= 75.0:
        agreement_level = "Strong"
    elif agreement_percentage >= 50.0:
        agreement_level = "Moderate"
    else:
        agreement_level = "Weak"
        
    execution_time_ms = (time.perf_counter() - start_time) * 1000.0
    
    logger.info(
        f"Agreement Engine Analysis Complete: Consensus='{consensus_pred}', "
        f"Agreement={agreement_percentage:.1f}% ({agreement_level}), "
        f"Executed={successful_count}/{total_models}, Failed={failed_count}, Latency={execution_time_ms:.2f}ms"
    )
    
    return ConsensusAnalysis(
        consensus_prediction=consensus_pred,
        agreement_percentage=round(agreement_percentage, 2),
        agreement_level=agreement_level,
        total_discovered_models=total_models,
        successfully_executed_models=successful_count,
        failed_models=failed_count,
        model_predictions=model_predictions
    )
