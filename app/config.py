"""Configuration constants for Smart Insole Backend"""

import os
from pathlib import Path

# Base paths
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DATABASE_PATH = DATA_DIR / "insole.db"

# Server configuration
BACKEND_HOST = os.getenv("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.getenv("BACKEND_PORT", "8000"))

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:8501",
    "http://127.0.0.1:8501",
    "http://localhost:8001",
    "http://127.0.0.1:8001",
]

# Signal processing parameters
SAMPLE_RATE = 500  # Hz - original sample rate from sensors
TARGET_RATE = 20  # Hz - target rate after decimation
LOWPASS_CUTOFF = 2.5  # Hz - Butterworth filter cutoff frequency
FILTER_ORDER = 4  # Butterworth filter order

# Step detection parameters
STEP_CHANNELS = [2, 4, 7]  # ch2, ch4, ch7 for step detection
PEAK_DISTANCE = 8  # minimum samples between peaks
PEAK_HEIGHT = 100  # minimum peak height threshold
SMOOTHING_WINDOW = 31  # window size for signal smoothing

# Heatmap parameters
PRESSURE_PERCENTILE_LOW = 90  # lower percentile for pressure calculation
PRESSURE_PERCENTILE_HIGH = 100  # upper percentile for pressure calculation
PRESSURE_MIN = 0  # minimum pressure value
PRESSURE_MAX = 999  # maximum pressure value

# Device IDs
DEVICE_LEFT = 1  # device_id for left insole
DEVICE_RIGHT = 2  # device_id for right insole

# Channel count
NUM_CHANNELS = 8  # ch0 through ch7

# Classification activities (for mock)
ACTIVITIES = ["walking", "sitting", "running"]
