"""
Finance Utility Suite
Configuration File
"""

from pathlib import Path

# ----------------------------
# Application
# ----------------------------

APP_NAME = "Finance Utility Suite"
APP_VERSION = "0.1.0"

# ----------------------------
# Window
# ----------------------------

WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 760

THEME = "System"
COLOR_THEME = "blue"

# ----------------------------
# Folder Structure
# ----------------------------

BASE_DIR = Path(__file__).resolve().parent

DATA_FOLDER = BASE_DIR / "data"
OUTPUT_FOLDER = BASE_DIR / "output"
LOG_FOLDER = BASE_DIR / "logs"
ASSET_FOLDER = BASE_DIR / "assets"

# Create folders automatically

for folder in [
    DATA_FOLDER,
    OUTPUT_FOLDER,
    LOG_FOLDER,
    ASSET_FOLDER
]:
    folder.mkdir(exist_ok=True)

# ----------------------------
# Report
# ----------------------------

REPORT_PREFIX = "Stock_Analysis"

AUTO_OPEN_REPORT = True

# ----------------------------
# Yahoo Finance
# ----------------------------

REQUEST_TIMEOUT = 15

MAX_RETRY = 3