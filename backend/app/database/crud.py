"""
crud.py
-------
Database read/write operations ("CRUD" = Create, Read, Update, Delete)
for prediction history. Keeps raw SQLAlchemy queries out of the API
route files.

WHICH file:
    backend/app/database/crud.py

HOW it connects to other files:
    - Uses the PredictionHistory model from models.py.
    - Called by api/routes/prediction.py (to save a new prediction),
      api/routes/history.py (to list/search/delete), and
      api/routes/statistics.py (to compute stats).
"""

from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.config import EMAIL_PREVIEW_LENGTH
from app.database.models import PredictionHistory


def create_prediction_record(
    db: Session,
    email_text: str,
    category: str,
    confidence: float,
    processing_time_ms: float,
) -> PredictionHistory:
    """Save a new prediction to history, storing only a short preview of
    the email (see models.py for why)."""
    preview = email_text[:EMAIL_PREVIEW_LENGTH]
    if len(email_text) > EMAIL_PREVIEW_LENGTH:
        preview += "..."

    record = PredictionHistory(
        email_preview=preview,
        category=category,
        confidence=confidence,
        processing_time_ms=processing_time_ms,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


def get_history(
    db: Session,
    search: Optional[str] = None,
    category: Optional[str] = None,
    sort_by: str = "newest",
    limit: int = 100,
    offset: int = 0,
):
    """List prediction history with optional search/filter/sort.

    sort_by options: "newest", "oldest", "highest_confidence", "lowest_confidence"
    """
    query = db.query(PredictionHistory)

    if search:
        query = query.filter(PredictionHistory.email_preview.ilike(f"%{search}%"))

    if category:
        query = query.filter(PredictionHistory.category == category.lower())

    sort_map = {
        "newest": PredictionHistory.created_at.desc(),
        "oldest": PredictionHistory.created_at.asc(),
        "highest_confidence": PredictionHistory.confidence.desc(),
        "lowest_confidence": PredictionHistory.confidence.asc(),
    }
    order_clause = sort_map.get(sort_by, PredictionHistory.created_at.desc())
    query = query.order_by(order_clause)

    total = query.count()
    items = query.offset(offset).limit(limit).all()
    return items, total


def delete_history_item(db: Session, item_id: int) -> bool:
    record = db.query(PredictionHistory).filter(PredictionHistory.id == item_id).first()
    if not record:
        return False
    db.delete(record)
    db.commit()
    return True


def delete_all_history(db: Session) -> int:
    count = db.query(PredictionHistory).count()
    db.query(PredictionHistory).delete()
    db.commit()
    return count


def get_statistics(db: Session) -> dict:
    """Compute dashboard statistics from prediction history."""
    total = db.query(PredictionHistory).count()

    if total == 0:
        return {
            "total_predictions": 0,
            "most_common_category": None,
            "spam_percentage": 0.0,
            "average_confidence": 0.0,
            "todays_predictions": 0,
            "category_breakdown": {},
        }

    category_counts = (
        db.query(PredictionHistory.category, func.count(PredictionHistory.id))
        .group_by(PredictionHistory.category)
        .all()
    )
    category_breakdown = {cat: count for cat, count in category_counts}
    most_common_category = max(category_breakdown, key=category_breakdown.get)

    spam_count = category_breakdown.get("spam", 0)
    spam_percentage = round((spam_count / total) * 100, 2)

    avg_confidence = db.query(func.avg(PredictionHistory.confidence)).scalar() or 0.0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    todays_predictions = (
        db.query(PredictionHistory)
        .filter(PredictionHistory.created_at >= today_start)
        .count()
    )

    return {
        "total_predictions": total,
        "most_common_category": most_common_category,
        "spam_percentage": spam_percentage,
        "average_confidence": round(float(avg_confidence), 4),
        "todays_predictions": todays_predictions,
        "category_breakdown": category_breakdown,
    }
