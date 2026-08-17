"""
model_loader.py
----------------
Loads the trained ML pipeline (from Day 1) ONCE and keeps it in memory,
instead of reloading it from disk on every API request.

WHAT are we doing?
    Using functools.lru_cache so the first call to get_model() loads the
    joblib file from disk, and every subsequent call returns the same
    already-loaded object instantly.

WHY does this matter?
    Loading a model from disk takes time (tens of milliseconds). If we
    reloaded it on every request, every /api/predict call would be
    slower than necessary, and under load this adds up fast. Loading it
    once at startup and reusing it is standard practice for serving ML
    models.

WHICH file:
    backend/app/ml/model_loader.py

HOW it connects to other files:
    - predict.py calls get_model() to get the pipeline + labels.
    - main.py calls get_model() once at startup so the first real
      request isn't slowed down by a cold load, and so we fail fast
      with a clear error if the model file is missing.
"""

from functools import lru_cache

import joblib

from app.config import MODEL_PATH


class ModelNotFoundError(RuntimeError):
    """Raised when the trained model file cannot be found on disk."""


@lru_cache(maxsize=1)
def get_model():
    """Load and cache the trained pipeline bundle.

    Returns a dict with:
        - "pipeline": the fitted sklearn Pipeline (TF-IDF + LogisticRegression)
        - "labels": the sorted list of category labels
    """
    if not MODEL_PATH.exists():
        raise ModelNotFoundError(
            f"Trained model not found at {MODEL_PATH}. "
            "Run 'python ml/src/train.py' from the project root first."
        )
    bundle = joblib.load(MODEL_PATH)
    return bundle
