"""
test_api.py
-----------
Tests for the FastAPI backend using FastAPI's TestClient (built on httpx).
These spin up the app in-memory — no need to run a live server.

Run with:
    cd backend
    pytest tests/ -v

NOTE: These tests use the same SQLite DB configured in app.config. For a
truly isolated test run in a bigger project you'd point DATABASE_URL at a
temporary/in-memory database via an env var or pytest fixture override;
kept simple here for a beginner-friendly Day 2 project.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert "model_loaded" in body


def test_valid_prediction():
    response = client.post(
        "/api/predict",
        json={"email_text": "Congratulations! You have won a $500 gift card. Click this link to claim your reward."},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "spam"
    assert 0.0 <= body["confidence"] <= 1.0
    assert "explanation" in body
    assert "processing_time_ms" in body
    assert "timestamp" in body
    assert "top_features" in body
    assert isinstance(body["top_features"], list)


def test_low_confidence_flag_is_boolean():
    response = client.post("/api/predict", json={"email_text": "Hello"})
    assert response.status_code == 200
    assert isinstance(response.json()["is_low_confidence"], bool)


def test_empty_email_rejected():
    response = client.post("/api/predict", json={"email_text": ""})
    assert response.status_code in (400, 422)


def test_whitespace_only_email_rejected():
    response = client.post("/api/predict", json={"email_text": "   "})
    assert response.status_code in (400, 422)


def test_extremely_long_email_rejected():
    huge_text = "a" * 20000  # over MAX_EMAIL_LENGTH
    response = client.post("/api/predict", json={"email_text": huge_text})
    assert response.status_code in (400, 422)


def test_invalid_request_body():
    response = client.post("/api/predict", json={"wrong_field": "hello"})
    assert response.status_code in (400, 422)


def test_history_endpoint_returns_list():
    # Make a prediction first so history has at least one entry.
    client.post("/api/predict", json={"email_text": "Your meeting has been moved to 3 PM tomorrow."})
    response = client.get("/api/history")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body
    assert body["total"] >= 1


def test_history_timestamps_include_utc_offset():
    # Regression test: history timestamps must always serialize with an
    # explicit UTC offset (e.g. "...+00:00"), otherwise a browser's
    # `new Date(...)` parses the offset-less string as LOCAL time instead
    # of UTC, silently showing the wrong time to any user not in UTC.
    client.post("/api/predict", json={"email_text": "Your meeting has been moved to 3 PM tomorrow."})
    response = client.get("/api/history", params={"limit": 1, "sort_by": "newest"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert len(items) >= 1
    created_at = items[0]["created_at"]
    assert created_at.endswith("+00:00") or created_at.endswith("Z"), (
        f"created_at is missing a UTC offset: {created_at!r}"
    )


def test_history_search_and_filter():
    response = client.get("/api/history", params={"category": "spam", "sort_by": "newest"})
    assert response.status_code == 200
    body = response.json()
    for item in body["items"]:
        assert item["category"] == "spam"


def test_statistics_endpoint():
    response = client.get("/api/statistics")
    assert response.status_code == 200
    body = response.json()
    assert "total_predictions" in body
    assert "average_confidence" in body
    assert "category_breakdown" in body


def test_delete_single_history_item():
    # Create one, then delete it by id.
    predict_response = client.post("/api/predict", json={"email_text": "Hey, are we still on for dinner?"})
    assert predict_response.status_code == 200

    history = client.get("/api/history", params={"limit": 1, "sort_by": "newest"}).json()
    item_id = history["items"][0]["id"]

    delete_response = client.delete(f"/api/history/{item_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["deleted"] is True


def test_delete_nonexistent_history_item_returns_404():
    response = client.delete("/api/history/999999999")
    assert response.status_code == 404


# --- Day 4: file upload tests -------------------------------------------

def test_upload_valid_txt_file():
    file_content = b"Congratulations! You have won a $500 gift card. Click this link to claim your reward."
    response = client.post(
        "/api/predict/upload",
        files={"file": ("email.txt", file_content, "text/plain")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "spam"
    assert "top_features" in body


def test_upload_valid_eml_file():
    eml_content = (
        b"From: sender@example.com\r\n"
        b"To: recipient@example.com\r\n"
        b"Subject: Meeting update\r\n"
        b"Content-Type: text/plain; charset=utf-8\r\n"
        b"\r\n"
        b"Your meeting has been moved to 3 PM tomorrow.\r\n"
    )
    response = client.post(
        "/api/predict/upload",
        files={"file": ("email.eml", eml_content, "message/rfc822")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "work"


def test_upload_rejects_invalid_extension():
    response = client.post(
        "/api/predict/upload",
        files={"file": ("email.pdf", b"not a real pdf", "application/pdf")},
    )
    assert response.status_code == 400


def test_upload_rejects_empty_file():
    response = client.post(
        "/api/predict/upload",
        files={"file": ("email.txt", b"", "text/plain")},
    )
    assert response.status_code == 400


def test_upload_rejects_oversized_file():
    huge_content = b"a" * (3 * 1024 * 1024)  # 3 MB, over the 2 MB limit
    response = client.post(
        "/api/predict/upload",
        files={"file": ("email.txt", huge_content, "text/plain")},
    )
    assert response.status_code == 400
