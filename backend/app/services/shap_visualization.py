import io
from typing import Any, Dict

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import shap

from app.core.logging_config import logger

# Use Agg backend for headless environments to prevent GUI thread issues
matplotlib.use("Agg")


def _build_shap_explanation(
    explanation_dict: Dict[str, Any], model_type: str
) -> shap.Explanation:
    """
    Constructs a shap.Explanation object from the raw explanation dictionary.
    """
    if model_type not in ["day", "folic"]:
        raise ValueError("model_type must be either 'day' or 'folic'")

    model_key = f"{model_type}_model"
    shap_key = f"{model_type}_shap_values"
    base_key = f"{model_type}_base_value"

    # Extract base value
    base_value = explanation_dict["explanation"][model_key]["base_value"]

    # Extract shap values and feature names aligned to the original inference order
    # Note: explanation_dict currently returns top_features sorted, but we need
    # to reconstruct the full 5-feature array from the original indices to map correctly.
    # Actually, if we just use the top_features array, we can visualize those top features.
    top_features = explanation_dict["explanation"][model_key]["top_features"]
    
    # We reconstruct the values for plotting
    values = []
    feature_names = []
    for f in top_features:
        values.append(f["shap_value"])
        feature_names.append(f["feature_name"])
        
    values_arr = np.array(values)
    
    return shap.Explanation(
        values=values_arr,
        base_values=base_value,
        feature_names=feature_names,
    )


def generate_waterfall_plot(explanation_dict: Dict[str, Any], model_type: str) -> bytes:
    """
    Generates a SHAP waterfall plot for the given model explanation.
    
    Returns:
        bytes: The PNG image bytes.
    """
    logger.info(f"Generating waterfall plot for {model_type} model")
    exp = _build_shap_explanation(explanation_dict, model_type)
    
    plt.figure(figsize=(8, 5))
    shap.plots.waterfall(exp, show=False)
    plt.title(f"SHAP Waterfall Plot ({model_type.title()} Model)")
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    
    return buf.getvalue()


def generate_bar_plot(explanation_dict: Dict[str, Any], model_type: str) -> bytes:
    """
    Generates a SHAP bar plot for the given model explanation.
    
    Returns:
        bytes: The PNG image bytes.
    """
    logger.info(f"Generating bar plot for {model_type} model")
    exp = _build_shap_explanation(explanation_dict, model_type)
    
    plt.figure(figsize=(8, 5))
    shap.plots.bar(exp, show=False)
    plt.title(f"SHAP Bar Plot ({model_type.title()} Model)")
    plt.tight_layout()
    
    buf = io.BytesIO()
    plt.savefig(buf, format="png", dpi=150, bbox_inches="tight")
    plt.close()
    
    return buf.getvalue()
