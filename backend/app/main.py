"""
main.py
-------
The FastAPI application entry point. This is what Uvicorn runs.

WHAT are we doing?
    1. Creating the FastAPI app.
    2. Enabling CORS so the Day 3 React frontend (running on a different
       port) is allowed to call this API from the browser.
    3. Creating database tables on startup if they don't exist.
    4. Registering all route modules (health, prediction, history, statistics)
       under the /api prefix.
    5. Adding consistent error handlers so clients always get clean JSON
       errors (404 / 400 / 500) instead of raw stack traces.

WHICH file:
    backend/app/main.py

HOW to run:
    cd backend
    uvicorn app.main:app --reload --port 8000

Then visit:
    http://localhost:8000/docs        (interactive API docs)
    http://localhost:8000/api/health  (health check)
"""

import logging

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import ALLOWED_ORIGINS
from app.database.database import Base, engine
from app.api.routes import health, history, prediction, statistics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("smartmail")

app = FastAPI(
    title="SmartMail API",
    description="AI email classifier — TF-IDF + Logistic Regression backend.",
    version="0.2.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    # Create the prediction_history table if it doesn't exist yet.
    # (For a real production app you'd use Alembic migrations instead,
    # but create_all() is perfectly fine for a project this size.)
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables ready.")


# --- Consistent error handling -------------------------------------------
# WHY? Without these, FastAPI's default error responses vary in shape,
# and unhandled exceptions leak raw Python stack traces to the client.
# We normalize everything to {"error": ..., "detail": ...}.

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": exc.detail if isinstance(exc.detail, str) else "Error", "detail": str(exc.detail)},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Raised automatically by Pydantic when a request body fails validation
    # (e.g. empty email_text, email_text too long, missing field).
    return JSONResponse(
        status_code=400,
        content={"error": "Validation error", "detail": exc.errors()},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "Something went wrong. Please try again."},
    )


# --- Routes -----------------------------------------------------------------
app.include_router(health.router, prefix="/api", tags=["Health"])
app.include_router(prediction.router, prefix="/api", tags=["Prediction"])
app.include_router(history.router, prefix="/api", tags=["History"])
app.include_router(statistics.router, prefix="/api", tags=["Statistics"])


@app.get("/")
def root():
    return {"message": "SmartMail API is running. See /docs for API documentation."}
