"""
health.py
---------
GET /api/health — a simple endpoint to check the API is up and the model
is loaded. Useful for uptime checks, Docker healthchecks, and quick
manual testing.

WHICH file:
    backend/app/api/routes/health.py
"""

from fastapi import APIRouter

from app.ml.model_loader import get_model, ModelNotFoundError

router = APIRouter()


@router.get("/health")
def health_check():
    model_loaded = True
    try:
        get_model()
    except ModelNotFoundError:
        model_loaded = False

    return {
        "status": "ok",
        "model_loaded": model_loaded,
    }
