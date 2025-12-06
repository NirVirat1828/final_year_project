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

```bash
pip install -r requirements.txt
```

---

## Folder Structure

> See directory tree at the top of this file for details.

---

## Model Overview

- Data preprocessing and peak detection for sensor signals
- Feature engineering for voltammetry data
- Supervised learning model with evaluation
- Optional: FastAPI/Flask app for deployment

---

## How to Run

1. Preprocess and extract features (run scripts in `src/data_preprocessing/`).
2. Model training in `src/modeling/` or via `notebooks/04_model_training.ipynb`.
3. Evaluate and visualize results in the respective notebooks and scripts.

---

## References

See `docs/references.bib` for literature used.
