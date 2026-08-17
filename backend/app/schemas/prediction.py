"""
schemas/prediction.py
----------------------
Pydantic models define the "shape" of data going in and out of the API.
FastAPI uses these to validate requests automatically and to generate
the interactive API docs at /docs.

WHY Pydantic?
    Without it, we'd have to manually check "is email_text present? Is it
    a string? Is it too long?" in every route. Pydantic does this
    automatically and returns a clean 422 error if the request doesn't
    match the schema.

WHICH file:
    backend/app/schemas/prediction.py

HOW it connects to other files:
    - api/routes/prediction.py uses PredictionRequest and PredictionResponse.
    - api/routes/history.py uses HistoryItem and HistoryResponse.
    - api/routes/statistics.py uses StatisticsResponse.
"""

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel, Field, field_validator

from app.config import MAX_EMAIL_LENGTH, MIN_EMAIL_LENGTH


class PredictionRequest(BaseModel):
    email_text: str = Field(
        ...,
        min_length=MIN_EMAIL_LENGTH,
        max_length=MAX_EMAIL_LENGTH,
        description="The raw email text to classify.",
    )

    @field_validator("email_text")
    @classmethod
    def not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("email_text cannot be empty or whitespace only.")
        return value


class PredictionResponse(BaseModel):
    category: str
    confidence: float
    processing_time_ms: float
    timestamp: datetime
    explanation: str
    is_low_confidence: bool
    all_scores: Dict[str, float]


class HistoryItem(BaseModel):
    id: int
    email_preview: str
    category: str
    confidence: float
    processing_time_ms: float
    created_at: datetime

    class Config:
        from_attributes = True  # allows creating this from a SQLAlchemy object


class HistoryResponse(BaseModel):
    items: List[HistoryItem]
    total: int


class StatisticsResponse(BaseModel):
    total_predictions: int
    most_common_category: Optional[str]
    spam_percentage: float
    average_confidence: float
    todays_predictions: int
    category_breakdown: Dict[str, int]


class DeleteResponse(BaseModel):
    deleted: bool
    detail: str


class ErrorResponse(BaseModel):
    error: str
    detail: str
