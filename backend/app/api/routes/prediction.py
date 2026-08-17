"""
prediction.py
--------------
POST /api/predict — the core endpoint. Takes email text, returns a
predicted category, confidence, explanation, processing time, and
timestamp. Also saves a preview of the prediction to history.

WHAT are we doing?
    1. FastAPI + Pydantic validate the incoming request automatically
       (empty email, too-long email, or a malformed body all get
       rejected with a 422 before this function even runs).
    2. Running the email through the ML pipeline (app.ml.predict).
    3. Saving a record to prediction history (app.database.crud).
    4. Returning a structured JSON response.

WHICH file:
    backend/app/api/routes/prediction.py

HOW to test it:
    curl -X POST http://localhost:8000/api/predict \\
      -H "Content-Type: application/json" \\
      -d '{"email_text": "Congratulations! You won a free prize."}'
"""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import LOW_CONFIDENCE_THRESHOLD
from app.database import crud
from app.database.database import get_db
from app.ml.predict import classify_email
from app.ml.model_loader import ModelNotFoundError
from app.schemas.prediction import PredictionRequest, PredictionResponse

router = APIRouter()


@router.post("/predict", response_model=PredictionResponse)
def predict(request: PredictionRequest, db: Session = Depends(get_db)):
    try:
        result = classify_email(request.email_text)
    except ModelNotFoundError:
        # 500: this is a server misconfiguration (model wasn't trained/found),
        # not something the client did wrong.
        raise HTTPException(
            status_code=500,
            detail="The ML model is not available on the server. Please contact the administrator.",
        )
    except ValueError as e:
        # 400: the client sent something we couldn't process (e.g. text
        # that becomes empty after cleaning, like only punctuation).
        raise HTTPException(status_code=400, detail=str(e))

    crud.create_prediction_record(
        db=db,
        email_text=request.email_text,
        category=result["category"],
        confidence=result["confidence"],
        processing_time_ms=result["processing_time_ms"],
    )

    return PredictionResponse(
        category=result["category"],
        confidence=result["confidence"],
        processing_time_ms=result["processing_time_ms"],
        timestamp=datetime.now(timezone.utc),
        explanation=result["explanation"],
        is_low_confidence=result["confidence"] < LOW_CONFIDENCE_THRESHOLD,
        all_scores=result["all_scores"],
    )
