# Final Year Project

## Project Overview

This repository contains the code and documentation for my final year project, which involves analysis and modeling based on sensor (voltammetry) data.

- **Raw data**: `data/raw/` contains all batches of sensor readings.
- **Processed data**: Feature extraction and final data used for model training.
- **Notebooks**: For data exploration, pre-processing, modeling, and visualization.
- **src/**: Modular Python code for the full project pipeline.
- **results/**: Model metrics, figures, and reports.
- **docs/**: Project documentation, architecture diagrams, and references.
- **tests/**: Test scripts for code modules.

---

## Setup

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Installation

1. Clone the repository:
```bash
git clone https://github.com/NirVirat1828/final_year_project.git
cd final_year_project
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
pytest tests/
```

---

## Directory Structure

```
final-year-project/
│
├── README.md                       # Full project explanation, setup steps, model overview
├── requirements.txt                # Python dependencies
├── .gitignore                      # Git ignore rules
│
├── data/
│   ├── raw/
│   │   ├── batch_1/                # Raw sensor data batch 1
│   │   ├── batch_2/                # Raw sensor data batch 2
│   │   ├── batch_3/                # Raw sensor data batch 3
│   │   ├── batch_4/                # Raw sensor data batch 4
│   │   └── batch_5/                # Raw sensor data batch 5
│   ├── processed/
│   │   ├── features_batch_1.csv    # Extracted features from batch 1
│   │   ├── features_batch_2.csv    # Extracted features from batch 2
│   │   └── combined_dataset.csv    # Final dataset used for training (gitignored)
│   └── synthetic/
│       └── simulated_batches/      # Synthetic data for testing
│
├── notebooks/
│   ├── 01_data_understanding.ipynb # Initial data exploration
│   ├── 02_preprocessing.ipynb      # Data cleaning and preprocessing
│   ├── 03_feature_engineering.ipynb# Feature extraction
│   ├── 04_model_training.ipynb     # Model training and tuning
│   ├── 05_evaluation.ipynb         # Model evaluation
│   └── 06_visualizations.ipynb     # Results visualization
│
├── src/
│   ├── data_preprocessing/
│   │   ├── load_data.py            # Data loading utilities
│   │   ├── clean_data.py           # Data cleaning functions
│   │   ├── peak_detection.py       # Peak detection algorithms
│   │   └── feature_extraction.py   # Feature engineering
│   ├── modeling/
│   │   ├── train_model.py          # Model training pipeline
│   │   ├── evaluate.py             # Model evaluation metrics
│   │   └── model_utils.py          # Utility functions for models
│   ├── utils/
│   │   ├── visualization.py        # Plotting and visualization
│   │   └── constants.py            # Project constants
│   └── app/
│       ├── api.py                  # REST API for model serving
│       ├── model.pkl               # Trained model (gitignored)
│       └── scaler.pkl              # Feature scaler (gitignored)
│
├── results/
│   ├── metrics/
│   │   ├── training_logs.json      # Training progress logs
│   │   └── model_scores.csv        # Model performance scores
│   ├── figures/
│   │   ├── voltammogram_plots/     # Sensor signal plots
│   │   ├── peak_plots/             # Peak detection visualizations
│   │   └── model_accuracy.png      # Model accuracy chart
│   └── reports/
│       ├── EDA_report.pdf          # Exploratory Data Analysis
│       ├── model_report.pdf        # Model performance report
│       └── deployment_plan.pdf     # Deployment documentation
│
├── docs/
│   ├── project_report/
│   │   └── FYP_Final_Report.docx   # Final project report
│   ├── ppt/
│   │   └── FYP_Presentation.pptx   # Project presentation
│   ├── diagrams/
│   │   ├── system_architecture.png # System architecture diagram
│   │   └── workflow.png            # Project workflow diagram
│   └── references.bib              # Bibliography
│
└── tests/
    ├── test_peak_detection.py      # Tests for peak detection
    ├── test_feature_extraction.py  # Tests for feature extraction
    └── test_model_training.py      # Tests for model training
```

---

## Model Overview

### Data Processing Pipeline

1. **Data Loading**: Raw voltammetry sensor data from multiple batches
2. **Preprocessing**: Noise filtering, outlier removal, and normalization
3. **Peak Detection**: Identification and characterization of signal peaks
4. **Feature Engineering**: Extraction of statistical and peak-based features

### Machine Learning

- Supervised learning approach for classification/regression
- Feature selection and dimensionality reduction
- Model training with hyperparameter tuning
- Cross-validation and performance evaluation
- Model persistence and versioning

### Deployment

- Optional: FastAPI/Flask REST API for model serving
- Containerization for reproducible deployment
- Model monitoring and logging

---

## How to Run

### 1. Data Preprocessing

```bash
# Option 1: Using Python scripts
python src/data_preprocessing/load_data.py
python src/data_preprocessing/clean_data.py
python src/data_preprocessing/feature_extraction.py

# Option 2: Using Jupyter notebooks
jupyter notebook notebooks/01_data_understanding.ipynb
```

### 2. Model Training

```bash
# Option 1: Using Python script
python src/modeling/train_model.py

# Option 2: Using Jupyter notebook
jupyter notebook notebooks/04_model_training.ipynb
```

### 3. Model Evaluation

```bash
# Option 1: Using Python script
python src/modeling/evaluate.py

# Option 2: Using Jupyter notebook
jupyter notebook notebooks/05_evaluation.ipynb
```

### 4. Visualization

```bash
# Generate visualizations
jupyter notebook notebooks/06_visualizations.ipynb
```

### 5. API Deployment (Optional)

```bash
# Run the API server
python src/app/api.py
```

---

## Testing

Run all tests:
```bash
pytest tests/
```

Run specific test file:
```bash
pytest tests/test_peak_detection.py
```

Run with coverage:
```bash
pytest --cov=src tests/
```

---

## Data Files

- Raw data should be placed in `data/raw/batch_X/` directories
- Processed features are saved in `data/processed/`
- Final combined dataset (`combined_dataset.csv`) is gitignored
- Model artifacts (`.pkl` files) are gitignored

---

## Results and Outputs

All results are saved in the `results/` directory:
- **Metrics**: Training logs and performance scores
- **Figures**: Plots and visualizations
- **Reports**: Generated PDF reports

Note: The `results/*` directory is gitignored to avoid committing large output files.

---

## Documentation

- **Project Report**: See `docs/project_report/FYP_Final_Report.docx`
- **Presentation**: See `docs/ppt/FYP_Presentation.pptx`
- **Architecture**: See diagrams in `docs/diagrams/`
- **References**: See `docs/references.bib` for literature used

---

## Contributing

1. Create a new branch for your feature
2. Make your changes
3. Run tests to ensure nothing is broken
4. Submit a pull request

---

## License

This project is part of an academic final year project.

---

## Contact

For questions or feedback, please contact the project maintainer.
