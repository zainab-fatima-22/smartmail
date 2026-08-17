"""
models.py
---------
SQLAlchemy ORM model for the prediction history table.

WHAT are we doing?
    Defining the `PredictionHistory` table: one row per email classified.

WHY do we store only a preview, not the full email?
    PRIVACY. Emails can contain sensitive personal information. Storing
    full email contents in a database that might end up in a demo,
    screenshot, or shared environment is a real privacy risk. Instead we
    store only a short preview (see config.EMAIL_PREVIEW_LENGTH,
    currently 80 characters) — enough to recognize an entry in the
    history list, not enough to reconstruct the original email.

    If a future version of this project ever needs to store full email
    text (e.g. for retraining on real user data), that would require:
    - explicit user consent,
    - encryption at rest,
    - a data retention/deletion policy,
    and should be treated as a significant design change, not a default.

WHICH file:
    backend/app/database/models.py

HOW it connects to other files:
    - database.py provides `Base`, which this model inherits from.
    - crud.py performs queries against this table.
    - main.py creates this table at startup via Base.metadata.create_all().
"""

from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Float, Integer, String

from app.database.database import Base


class PredictionHistory(Base):
    __tablename__ = "prediction_history"

    id = Column(Integer, primary_key=True, index=True)
    email_preview = Column(String(120), nullable=False)  # truncated, NOT full email
    category = Column(String(30), nullable=False, index=True)
    confidence = Column(Float, nullable=False)
    processing_time_ms = Column(Float, nullable=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), index=True)
