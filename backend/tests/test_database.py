"""
test_database.py
-----------------
Tests the database CRUD layer (app/database/crud.py) directly, against
an isolated in-memory SQLite database — NOT the app's real database file
and NOT going through the HTTP API. This is what "Database" testing
means as its own category (separate from test_api.py, which tests the
API layer end-to-end and happens to exercise the database indirectly).

WHY an isolated in-memory database?
    Using the real backend/smartmail.db would mix test data with real
    usage data, and running tests twice would see leftover rows from the
    first run. An in-memory SQLite database (":memory:") is created fresh
    for every test and disappears when the connection closes — perfectly
    isolated, and fast.

Run with:
    cd backend
    pytest tests/test_database.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import crud
from app.database.database import Base


@pytest.fixture()
def db_session():
    """A fresh in-memory SQLite database + session for each test."""
    engine = create_engine("sqlite:///:memory:", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    TestSession = sessionmaker(bind=engine)
    session = TestSession()
    try:
        yield session
    finally:
        session.close()


def test_create_prediction_record_truncates_long_email(db_session):
    long_email = "a" * 500
    record = crud.create_prediction_record(
        db_session, email_text=long_email, category="work", confidence=0.9, processing_time_ms=1.2
    )
    # Privacy: only a preview should ever be stored, never the full text.
    assert len(record.email_preview) < len(long_email)
    assert record.email_preview.endswith("...")


def test_create_prediction_record_short_email_not_truncated(db_session):
    short_email = "Hi there"
    record = crud.create_prediction_record(
        db_session, email_text=short_email, category="personal", confidence=0.8, processing_time_ms=1.0
    )
    assert record.email_preview == short_email
    assert not record.email_preview.endswith("...")


def test_get_history_empty_database_returns_empty_list(db_session):
    items, total = crud.get_history(db_session)
    assert items == []
    assert total == 0


def test_get_history_search_filters_by_preview_text(db_session):
    crud.create_prediction_record(db_session, "Meeting at 3pm", "work", 0.9, 1.0)
    crud.create_prediction_record(db_session, "Win a free prize", "spam", 0.9, 1.0)

    items, total = crud.get_history(db_session, search="meeting")
    assert total == 1
    assert "Meeting" in items[0].email_preview


def test_get_history_category_filter(db_session):
    crud.create_prediction_record(db_session, "Meeting at 3pm", "work", 0.9, 1.0)
    crud.create_prediction_record(db_session, "Win a free prize", "spam", 0.9, 1.0)

    items, total = crud.get_history(db_session, category="spam")
    assert total == 1
    assert items[0].category == "spam"


def test_get_history_sort_by_confidence(db_session):
    crud.create_prediction_record(db_session, "Low confidence email", "work", 0.3, 1.0)
    crud.create_prediction_record(db_session, "High confidence email", "work", 0.95, 1.0)

    items, _ = crud.get_history(db_session, sort_by="highest_confidence")
    assert items[0].confidence == 0.95
    assert items[1].confidence == 0.3

    items, _ = crud.get_history(db_session, sort_by="lowest_confidence")
    assert items[0].confidence == 0.3


def test_get_history_pagination(db_session):
    for i in range(5):
        crud.create_prediction_record(db_session, f"Email {i}", "work", 0.9, 1.0)

    items_page1, total = crud.get_history(db_session, limit=2, offset=0)
    assert total == 5
    assert len(items_page1) == 2

    items_page2, _ = crud.get_history(db_session, limit=2, offset=2)
    assert len(items_page2) == 2

    # Pages must not overlap — every id across both pages should be unique.
    # (Not asserting a specific order here: records created in a tight
    # loop can share the same timestamp at datetime.now()'s resolution,
    # so "newest first" ordering among ties isn't guaranteed — only that
    # pagination itself doesn't duplicate or skip rows.)
    ids_page1 = {item.id for item in items_page1}
    ids_page2 = {item.id for item in items_page2}
    assert ids_page1.isdisjoint(ids_page2)


def test_delete_history_item_removes_record(db_session):
    record = crud.create_prediction_record(db_session, "Delete me", "spam", 0.9, 1.0)
    deleted = crud.delete_history_item(db_session, record.id)
    assert deleted is True

    items, total = crud.get_history(db_session)
    assert total == 0


def test_delete_history_item_nonexistent_returns_false(db_session):
    deleted = crud.delete_history_item(db_session, 999999)
    assert deleted is False


def test_delete_all_history_removes_everything(db_session):
    for i in range(3):
        crud.create_prediction_record(db_session, f"Email {i}", "work", 0.9, 1.0)

    count = crud.delete_all_history(db_session)
    assert count == 3

    items, total = crud.get_history(db_session)
    assert total == 0


def test_get_statistics_empty_database(db_session):
    stats = crud.get_statistics(db_session)
    assert stats["total_predictions"] == 0
    assert stats["most_common_category"] is None
    assert stats["spam_percentage"] == 0.0
    assert stats["category_breakdown"] == {}


def test_get_statistics_computes_correct_breakdown(db_session):
    crud.create_prediction_record(db_session, "Spam 1", "spam", 0.9, 1.0)
    crud.create_prediction_record(db_session, "Spam 2", "spam", 0.8, 1.0)
    crud.create_prediction_record(db_session, "Work 1", "work", 0.95, 1.0)

    stats = crud.get_statistics(db_session)
    assert stats["total_predictions"] == 3
    assert stats["most_common_category"] == "spam"
    assert stats["spam_percentage"] == pytest.approx(66.67, abs=0.1)
    assert stats["category_breakdown"] == {"spam": 2, "work": 1}
    assert stats["average_confidence"] == pytest.approx((0.9 + 0.8 + 0.95) / 3, abs=0.001)
