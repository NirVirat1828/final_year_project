# Electronic Tongue Orange Freshness API

![Orange Freshness API Banner](https://via.placeholder.com/1000x200?text=Orange+Freshness+Predictor+API)

## 1. Project Overview

### Problem Statement
The agriculture and food storage industries face significant challenges in accurately assessing the freshness and nutritional quality of produce during storage. Traditional chemical analysis is destructive, expensive, and time-consuming.

### Motivation
Electronic tongue sensors provide rapid, non-destructive electrochemical readings. However, translating raw sensor potentials into actionable business metrics (like remaining shelf life and nutritional degradation) requires robust machine learning models capable of handling complex non-linear relationships.

### Solution
This project implements a high-performance **FastAPI Backend** that wraps two Scikit-Learn Random Forest models. The models ingest an 11-feature sensor array to simultaneously predict the **Storage Age (Days)** and **Folic Acid Concentration (μM)**. A comprehensive SHAP (SHapley Additive exPlanations) integration layer provides human-readable explanations of *why* the model made its predictions, fostering trust and operational transparency.

---

## 2. System Architecture

```mermaid
flowchart TD
    Client((Client)) -->|InferenceRequest| Router(FastAPI Router)
    Router -->|Validation| Endpoints(API Endpoints)
    
    subgraph Service Layer
        Endpoints --> GradingService[Grading Service]
        Endpoints --> ExplainService[Explain Service]
        Endpoints --> VisService[Visualization Service]
    end
    
    subgraph ML Engine Layer
        GradingService --> MLEngine[ML Engine Singleton]
        ExplainService --> MLEngine
        VisService --> ExplainService
        
        MLEngine --> Preprocessing[StandardScaler & RFE]
        Preprocessing --> DayModel[RandomForest: Day]
        Preprocessing --> FolicModel[RandomForest: Folic]
        
        DayModel --> SHAPDay[TreeExplainer: Day]
        FolicModel --> SHAPFolic[TreeExplainer: Folic]
    end

    MLEngine -->|Raw Arrays| Service Layer
    Service Layer -->|Pydantic Models| Router
    Router -->|JSON / PNG| Client
```

### Components
* **FastAPI Router**: Handles HTTP transport, request validation (via Pydantic), and Swagger UI generation.
* **Service Layer**: Translates raw ML outputs into business metrics (e.g., categorical freshness grades, feature ranking).
* **ML Engine Layer**: A thread-safe Singleton managing the lifecycle of Scikit-Learn `.pkl` models and SHAP `TreeExplainers`, guaranteeing zero-duplicate preprocessing and high concurrency throughput.

---

## 3. Project Structure

```text
backend/
├── app/
│   ├── api/
│   │   └── endpoints.py          # Thin REST controllers (/analyze-batch, /explain)
│   ├── core/
│   │   ├── config.py             # Model versioning and environment configs
│   │   ├── logging_config.py     # Production stdout logger
│   │   └── ml_engine.py          # ML Singleton and SHAP compute layer
│   ├── schemas/
│   │   └── payload.py            # Strict Pydantic interface validations
│   └── services/
│       ├── explain_service.py    # Explanation formatting and feature ranking
│       ├── grading_service.py    # Business rules mapping days to freshness grades
│       └── shap_visualization.py # Matplotlib visual generator for SHAP data
├── models/                       # Serialized Scikit-Learn artifacts
└── requirements.txt
tests/                            # Pytest integration & unit testing suite
```

---

## 4. Technology Stack

* **Python 3.13** - Core runtime
* **FastAPI** - High-performance asynchronous web framework
* **Pydantic V2** - Strict data validation and settings management
* **scikit-learn** - Machine learning predictive modeling and preprocessing
* **SHAP** - Game-theoretic approach to explain model output
* **NumPy** - High-performance array computing
* **Matplotlib** - Headless generation of analytical plots
* **Joblib** - Efficient binary serialization of model artifacts
* **Pytest** - Automated testing suite

---

## 5. Features

* **Dual Prediction**: Simultaneously calculates estimated storage age and remaining folic acid levels.
* **Business Grading**: Automatically categorizes oranges into `A`, `B`, `C`, or `Reject` based on predicted shelf life.
* **Explainable AI (XAI)**: Full SHAP integration ranking the Top 3 contributing electrochemical features for every prediction.
* **Visual Diagnostics**: Dynamically generates Waterfall and Bar charts of the model's decision process directly over REST.
* **Production Observability**: Configured with strict JSON-compliant loggers capturing inference latency and batch identifiers.
* **Interactive Swagger UI**: Explore and test the API directly from the browser.

---

## 6. Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/your-org/orange-freshness-api.git
   cd orange-freshness-api/backend
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the server:**
   ```bash
   uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
   ```

---

## 7. API Documentation

Once the server is running, visit `http://127.0.0.1:8000/docs` to interact with the **Swagger UI**.

### `POST /api/v1/analyze-batch`
Standard inference endpoint. Returns freshness grading and estimated shelf life.
**Request Example:**
```json
{
  "batch_id": "batch-8472",
  "sensor_readings": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0]
}
```

### `POST /api/v1/explain`
Returns predictions mapped alongside SHAP-calculated feature importances.
**Response Highlight:**
```json
"explanation": {
  "day_model": {
    "base_value": 6.84,
    "top_features": [
      {
        "rank": 1,
        "feature_name": "DCT_3",
        "shap_value": -3.64,
        "absolute_importance": 3.64,
        "impact": "decrease"
      }
    ]
  }
}
```

### `POST /api/v1/explain/visualize`
Returns a `image/png` buffer rendering the mathematical decision boundary.
Accepts Query Parameters: `?model=day&plot_type=waterfall`

---

## 8. SHAP Explainability

**What is SHAP?**
SHAP (SHapley Additive exPlanations) is a game-theoretic approach to explaining the output of any machine learning model. It connects optimal credit allocation with local explanations using the classic Shapley values from cooperative game theory.

**Why is it used?**
Random Forests are powerful but notoriously "black box" in nature. SHAP opens the box by explicitly attributing a numerical value to each input feature, calculating exactly how much that feature pushed the prediction away from the model's average base expectation.

**How to Interpret the Visualizations:**
* **Waterfall Plots:** Start from the bottom (the `base_value` representing the average prediction over the training set). Each row shows a feature adding to (red) or subtracting from (blue) the prediction until reaching the final `f(x)` output at the top.
* **Bar Plots:** A simpler magnitude-based ranking. Longer bars represent features that had a higher absolute impact on the current specific prediction.

---

## 9. Screenshots

*Placeholder for Swagger UI*
![Swagger UI Placeholder](https://via.placeholder.com/800x400?text=Swagger+UI+Documentation)

*Placeholder for Waterfall Plot*
![Waterfall Plot Placeholder](https://via.placeholder.com/600x400?text=SHAP+Waterfall+Plot)

---

## 10. Running Tests

The application is heavily tested using `pytest`. The suite covers protocol validations, schema enforcements, mock-injections, and calculation logic.

```bash
cd ..
pytest tests/ -v
```

---

## 11. Future Improvements

* **Batch Explainability Endpoint:** Support lists of 2D sensor readings utilizing `.shap_values()` batch arrays to handle entire shipments in a single call.
* **Continuous Model Retraining Pipeline:** Integrate a DAG scheduler (like Airflow or Prefect) to periodically retrain the `.pkl` models to handle data drift and eliminate scikit-learn versioning warnings.
* **Containerization:** Wrap the backend inside a lightweight `Dockerfile` for seamless Kubernetes deployment.
* **Monitoring:** Hook the custom python `logger` into Prometheus and Grafana for real-time latency and prediction distribution tracking.
