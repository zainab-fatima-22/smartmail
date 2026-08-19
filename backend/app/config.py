"""
config.py
---------
Central place for configuration values (paths, limits, DB URL).

WHAT are we doing?
    Defining settings as plain constants, sourced from environment
    variables where it makes sense, with sensible defaults.

WHY?
    Hardcoding paths/limits throughout the codebase makes them hard to
    change and easy to get out of sync. Keeping them in one file means
    every other module imports from here instead of repeating values.

WHICH file:
    backend/app/config.py

HOW it connects to other files:
    - ml/model_loader.py uses MODEL_PATH to find the trained model.
    - database/database.py uses DATABASE_URL to connect to SQLite.
    - api/routes/prediction.py uses MAX_EMAIL_LENGTH for validation.
"""

import os
from pathlib import Path

# backend/app/config.py -> parents[0]=app, [1]=backend, [2]=smartmail root
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Where the Day 1 trained model lives. Can be overridden with an env var,
# e.g. in a Docker container where paths differ.
MODEL_PATH = Path(
    os.getenv("MODEL_PATH", str(PROJECT_ROOT / "ml" / "models" / "email_classifier.joblib"))
)

# SQLite database file lives inside backend/ so it's easy to find and .gitignore'd.
DATABASE_URL = os.getenv(
    "DATABASE_URL", f"sqlite:///{PROJECT_ROOT / 'backend' / 'smartmail.db'}"
)

# Validation limits for incoming prediction requests.
MIN_EMAIL_LENGTH = 1
MAX_EMAIL_LENGTH = int(os.getenv("MAX_EMAIL_LENGTH", "10000"))  # characters

# File upload limits (Day 4 — email file upload feature).
ALLOWED_UPLOAD_EXTENSIONS = {".txt", ".eml"}
MAX_UPLOAD_SIZE_BYTES = int(os.getenv("MAX_UPLOAD_SIZE_BYTES", str(2 * 1024 * 1024)))  # 2 MB

# How many top contributing words to include in a prediction's explanation.
TOP_FEATURES_COUNT = 5

# Below this confidence, the frontend/backend flags the prediction as low-confidence.
LOW_CONFIDENCE_THRESHOLD = float(os.getenv("LOW_CONFIDENCE_THRESHOLD", "0.6"))

# How much of the email to store in prediction history (privacy: we do NOT
# store full email contents by default, see database/models.py).
EMAIL_PREVIEW_LENGTH = 80

# CORS: which frontend origins are allowed to call this API.
ALLOWED_ORIGINS = os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
