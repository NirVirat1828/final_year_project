# Repository Scaffold

## Layout

- `src/preprocessing/` - feature extraction, feature selection, and preprocessing pipelines.
- `src/training/` - model training and stacking experiments.
- `src/benchmarking/` - blind-test evaluation, tournament runs, and comparison scripts.
- `src/inference/` - prediction entrypoints and inference helpers.
- `src/visualization/` - dashboard and presentation figure generation.
- `src/evaluation/` - shelf-life and downstream evaluation utilities.
- `docs/reports/` - project reports, summaries, and write-ups.
- `docs/guides/` - repository navigation and workflow notes.

## Import Rule

Run scripts from the project root so imports like `from src.preprocessing.track_a_preprocessing import TrackAPreprocessor` resolve correctly.

## Suggested Entrypoints

- `python -m src.training.track_a_train_classifier`
- `python -m src.inference.track_a_inference`
- `python -m src.benchmarking.blind_test_evaluation`
