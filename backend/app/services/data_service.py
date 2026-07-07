import pandas as pd
import random
import math
from pathlib import Path
from app.core.logging_config import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent
DATASETS_DIR = PROJECT_ROOT / "datasets"
RESULTS_DIR = PROJECT_ROOT / "outputs" / "results"

def get_paginated_dataset(page: int, page_size: int):
    """Reads X_features.csv and y_targets.csv and returns a paginated slice."""
    features_path = DATASETS_DIR / "X_features.csv"
    targets_path = DATASETS_DIR / "y_targets.csv"
    
    if not features_path.exists() or not targets_path.exists():
        logger.warning("Dataset files not found")
        return {"data": [], "total_records": 0, "page": page, "page_size": page_size}
        
    try:
        df_x = pd.read_csv(features_path)
        df_y = pd.read_csv(targets_path)
        
        # Merge them
        df = pd.concat([df_x, df_y], axis=1)
        total_records = len(df)
        
        start_idx = (page - 1) * page_size
        end_idx = start_idx + page_size
        
        subset = df.iloc[start_idx:end_idx].copy()
        
        # Replace NaN with None so FastAPI can serialize to JSON null
        import numpy as np
        subset = subset.replace({np.nan: None})
        data = subset.to_dict(orient="records")
        
        return {
            "data": data,
            "total_records": total_records,
            "page": page,
            "page_size": page_size
        }
    except Exception as e:
        logger.error(f"Error reading dataset: {e}")
        raise ValueError("Failed to read dataset")


def get_model_benchmarks():
    """Reads results_comparison.csv and returns formatted metrics for the UI."""
    results_path = RESULTS_DIR / "results_comparison.csv"
    
    if not results_path.exists():
        logger.warning(f"Benchmark results not found at {results_path}")
        return []
        
    try:
        df = pd.read_csv(results_path)
        # We only want Classification models for the Battle Arena radar chart right now.
        # The frontend radar chart typically compares algorithms on specific metrics.
        classification_df = df[df["Track"] == "Classification"]
        
        metrics = []
        for _, row in classification_df.iterrows():
            metrics.append({
                "model": row["Algorithm"].split("_", 1)[1] if "_" in row["Algorithm"] else row["Algorithm"],
                "Accuracy": round(float(row["Accuracy"]) * 100, 1) if pd.notna(row["Accuracy"]) else 0,
                "F1 Score": round(float(row["F1_Weighted"]) * 100, 1) if pd.notna(row["F1_Weighted"]) else 0,
                "preprocessing": row["Preprocessing"]
            })
            
        return metrics
    except Exception as e:
        logger.error(f"Error reading benchmark results: {e}")
        raise ValueError("Failed to read benchmark results")


def simulate_hardware_scan():
    """Samples a random row from X_features.csv to simulate an e-tongue scan."""
    features_path = DATASETS_DIR / "X_features.csv"
    
    if not features_path.exists():
        logger.warning(f"Features dataset not found at {features_path}")
        # Fallback to generic random array
        return [round(random.uniform(0.1, 10.0), 4) for _ in range(11)]
        
    try:
        df = pd.read_csv(features_path)
        # We only want the 11 feature columns if possible, but X_features.csv should contain them
        sample = df.sample(1).iloc[0]
        
        # Ensure we return exactly 11 numeric features in an array
        features_array = sample.values.tolist()
        
        # If there are non-numeric columns like ID, drop them.
        # Assuming X_features contains only features. If it contains batch_id, we filter it out.
        # Also replace NaN values with 0.0 to prevent JSON serialization errors.
        features_array = [
            0.0 if (isinstance(x, (int, float)) and math.isnan(x)) else float(x)
            for x in features_array
            if isinstance(x, (int, float))
        ]
        
        if len(features_array) > 11:
            features_array = features_array[:11]
        elif len(features_array) < 11:
            # Pad if somehow shorter
            features_array.extend([0.0] * (11 - len(features_array)))
            
        return features_array
    except Exception as e:
        logger.error(f"Error reading features dataset: {e}")
        return [round(random.uniform(0.1, 10.0), 4) for _ in range(11)]
