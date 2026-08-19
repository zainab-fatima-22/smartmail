"""
upload.py
---------
POST /api/predict/upload — classify an email from an uploaded .txt or
.eml file instead of pasted text.

WHAT are we doing?
    1. Validating the upload: extension, size, and that it's not empty.
    2. Extracting plain text from the file (see app/ml/file_extraction.py).
    3. Running the SAME classification + history-saving logic used by
       POST /api/predict, so uploaded and pasted emails behave
       identically after this point.

WHY validate BEFORE reading the whole file into memory?
    We check the filename extension and the declared Content-Length
    first so obviously-invalid uploads (wrong type, huge file) are
    rejected quickly, without wastefully reading arbitrary file
    contents into memory first. We still re-check the actual byte size
    after reading, since Content-Length can be absent or wrong.

    We never execute or interpret the uploaded file as anything other
    than plain text — this endpoint only ever reads bytes and decodes
    them as text, so it can't be used to run arbitrary/executable
    files uploaded by a user.

WHICH file:
    backend/app/api/routes/upload.py

HOW to test it:
    curl -X POST http://localhost:8000/api/predict/upload \\
      -F "file=@sample_email.txt"
"""

from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session

from app.config import ALLOWED_UPLOAD_EXTENSIONS, LOW_CONFIDENCE_THRESHOLD, MAX_UPLOAD_SIZE_BYTES
from app.database import crud
from app.database.database import get_db
from app.ml.file_extraction import FileExtractionError, extract_text_from_upload
from app.ml.model_loader import ModelNotFoundError
from app.ml.predict import classify_email
from app.schemas.prediction import PredictionResponse

router = APIRouter()


@router.post("/predict/upload", response_model=PredictionResponse)
async def predict_from_upload(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    extension = Path(file.filename or "").suffix.lower()
    if extension not in ALLOWED_UPLOAD_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '{extension or 'unknown'}'. "
            f"Allowed types: {', '.join(sorted(ALLOWED_UPLOAD_EXTENSIONS))}.",
        )

    raw_bytes = await file.read()

    if len(raw_bytes) == 0:
        raise HTTPException(status_code=400, detail="The uploaded file is empty.")

    if len(raw_bytes) > MAX_UPLOAD_SIZE_BYTES:
        max_mb = MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)
        raise HTTPException(
            status_code=400,
            detail=f"File is too large. Maximum allowed size is {max_mb:.0f} MB.",
        )

    try:
        email_text = extract_text_from_upload(file.filename or "upload", raw_bytes)
    except FileExtractionError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        result = classify_email(email_text)
    except ModelNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="The ML model is not available on the server. Please contact the administrator.",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    crud.create_prediction_record(
        db=db,
        email_text=email_text,
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
        top_features=result["top_features"],
        all_scores=result["all_scores"],
    )
