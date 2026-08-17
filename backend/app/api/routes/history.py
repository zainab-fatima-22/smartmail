"""
history.py
----------
GET /api/history — list past predictions, with search/filter/sort.
DELETE /api/history — clear all history.
DELETE /api/history/{id} — delete a single history entry.

WHICH file:
    backend/app/api/routes/history.py
"""

from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import crud
from app.database.database import get_db
from app.schemas.prediction import DeleteResponse, HistoryItem, HistoryResponse

router = APIRouter()


@router.get("/history", response_model=HistoryResponse)
def list_history(
    search: Optional[str] = Query(None, description="Search within email preview text"),
    category: Optional[str] = Query(None, description="Filter by category"),
    sort_by: str = Query(
        "newest",
        description="One of: newest, oldest, highest_confidence, lowest_confidence",
    ),
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    items, total = crud.get_history(
        db, search=search, category=category, sort_by=sort_by, limit=limit, offset=offset
    )
    return HistoryResponse(
        items=[HistoryItem.model_validate(item) for item in items],
        total=total,
    )


@router.delete("/history/{item_id}", response_model=DeleteResponse)
def delete_one(item_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_history_item(db, item_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"History item {item_id} not found.")
    return DeleteResponse(deleted=True, detail=f"Deleted history item {item_id}.")


@router.delete("/history", response_model=DeleteResponse)
def delete_all(db: Session = Depends(get_db)):
    count = crud.delete_all_history(db)
    return DeleteResponse(deleted=True, detail=f"Deleted {count} history item(s).")
