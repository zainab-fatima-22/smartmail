"""
statistics.py
-------------
GET /api/statistics — dashboard numbers: total predictions, most common
category, spam percentage, average confidence, today's predictions,
and a per-category breakdown (used for charts on Day 3).

WHICH file:
    backend/app/api/routes/statistics.py
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import crud
from app.database.database import get_db
from app.schemas.prediction import StatisticsResponse

router = APIRouter()


@router.get("/statistics", response_model=StatisticsResponse)
def statistics(db: Session = Depends(get_db)):
    stats = crud.get_statistics(db)
    return StatisticsResponse(**stats)
