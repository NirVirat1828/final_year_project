"""
Constants module.

This module defines constants used throughout the project.
"""

import os

# Get the project root directory (assumes constants.py is in src/utils/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Data paths
RAW_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'raw')
PROCESSED_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'processed')
SYNTHETIC_DATA_PATH = os.path.join(PROJECT_ROOT, 'data', 'synthetic')

# Model paths
MODEL_SAVE_PATH = os.path.join(PROJECT_ROOT, 'src', 'app')
RESULTS_PATH = os.path.join(PROJECT_ROOT, 'results')

# Data processing constants
SAMPLING_RATE = 1000  # Hz
SIGNAL_LENGTH = 5000  # samples

# Peak detection parameters
PEAK_THRESHOLD = 0.5
MIN_PEAK_DISTANCE = 10
NOISE_FILTER_METHOD = 'savgol'

# Model training parameters
TEST_SIZE = 0.2
RANDOM_STATE = 42
CV_FOLDS = 5

# Feature engineering
STATISTICAL_FEATURES = ['mean', 'std', 'min', 'max', 'skewness', 'kurtosis']
PEAK_FEATURES = ['peak_height', 'peak_width', 'peak_area', 'num_peaks']

# Visualization settings
FIGURE_SIZE = (10, 6)
DPI = 300
COLOR_PALETTE = 'viridis'
