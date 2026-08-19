# SmartMail API Documentation

Base URL (local development): `http://localhost:8000`

FastAPI also auto-generates interactive docs at `/docs` (Swagger UI) and
`/redoc` once the server is running — this file is a human-readable
companion to those.

All endpoints are under the `/api` prefix.

---

## GET /api/health

Check whether the API and the ML model are up.

**Response 200**
```json
{
  "status": "ok",
  "model_loaded": true
}
```

---

## POST /api/predict

Classify a single email.

**Request body**
```json
{
  "email_text": "Congratulations! You have won a $500 gift card. Click this link to claim your reward."
}
```

**Validation**
- `email_text` is required, 1–10,000 characters, and cannot be blank/whitespace-only.
- Invalid bodies return `400` with a JSON error (see Error format below).

**Response 200**
```json
{
  "category": "spam",
  "confidence": 0.9722,
  "processing_time_ms": 3.42,
  "timestamp": "2026-08-13T10:15:00.123456+00:00",
  "explanation": "The email contains promotional/scam-like language and urgency patterns commonly seen in spam.",
  "is_low_confidence": false,
  "top_features": [
    { "word": "claim", "weight": 0.3879 },
    { "word": "click", "weight": 0.3644 },
    { "word": "won", "weight": 0.2564 }
  ],
  "all_scores": {
    "spam": 0.9722,
    "promotional": 0.0104,
    "work": 0.0031,
    "personal": 0.0028,
    "important": 0.0087,
    "social": 0.0028
  }
}
```

- `is_low_confidence` is `true` when `confidence` is below the configured
  threshold (default 0.6, see `backend/app/config.py`). The frontend uses
  this to show a "low confidence" warning.
- `top_features` lists the words in this email that contributed most to
  the prediction, derived from the Logistic Regression coefficients for
  the predicted category multiplied by each word's TF-IDF score in this
  email. **These are model-associated features, not proof the email
  truly belongs to that category.**
- Every successful prediction is also saved to history (with only a short
  preview of the email — see Privacy section).

---

## POST /api/predict/upload

Classify an email from an uploaded file instead of pasted text.

**Request:** `multipart/form-data` with a single field `file`.

**Accepted file types:** `.txt`, `.eml` (max 2 MB, configurable via
`MAX_UPLOAD_SIZE_BYTES`).

For `.eml` files, the plain-text (or HTML, stripped of tags) message body
is extracted — headers like `From`/`Subject` are not sent to the
classifier.

```bash
curl -X POST http://localhost:8000/api/predict/upload \
  -F "file=@sample_email.txt"
```

**Response:** identical shape to `POST /api/predict` (see above).

**Errors:**
- `400` — unsupported extension, empty file, or file over the size limit.
- `500` — model not available.

---

## GET /api/history

List past predictions, newest first by default.

**Query parameters** (all optional)
| Param      | Type   | Description                                              |
|------------|--------|-----------------------------------------------------------|
| `search`   | string | Case-insensitive search within the stored email preview  |
| `category` | string | Filter to one category (e.g. `spam`)                      |
| `sort_by`  | string | `newest` (default), `oldest`, `highest_confidence`, `lowest_confidence` |
| `limit`    | int    | Max results to return (default 100, max 500)              |
| `offset`   | int    | Pagination offset (default 0)                              |

**Response 200**
```json
{
  "items": [
    {
      "id": 12,
      "email_preview": "Congratulations! You have won a $500 gift card...",
      "category": "spam",
      "confidence": 0.9722,
      "processing_time_ms": 3.42,
      "created_at": "2026-08-13T10:15:00.123456+00:00"
    }
  ],
  "total": 1
}
```

---

## DELETE /api/history/{id}

Delete a single history entry by id.

- `200` with `{"deleted": true, "detail": "..."}` on success.
- `404` if the id doesn't exist.

## DELETE /api/history

Delete **all** history entries. The frontend should confirm this with the
user before calling it (there's no undo).

**Response 200**
```json
{ "deleted": true, "detail": "Deleted 42 history item(s)." }
```

---

## GET /api/statistics

Dashboard summary numbers, computed from history.

**Response 200**
```json
{
  "total_predictions": 42,
  "most_common_category": "work",
  "spam_percentage": 14.29,
  "average_confidence": 0.83,
  "todays_predictions": 5,
  "category_breakdown": {
    "work": 15,
    "spam": 6,
    "promotional": 8,
    "personal": 5,
    "important": 4,
    "social": 4
  }
}
```

---

## Error format

All errors (400, 404, 422→normalized to 400, 500) return the same JSON shape:

```json
{
  "error": "Short error type",
  "detail": "Human-readable explanation (or validation error details)"
}
```

Stack traces are never returned to the client — unexpected errors are
logged server-side and returned as a generic 500 message instead.

---

## Privacy note

Prediction history stores only a short preview of each email (first 80
characters), never the full text. This is a deliberate design decision —
see the docstring in `backend/app/database/models.py` for details.
