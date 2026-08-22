# SmartMail backend — FastAPI + the trained ML model.
#
# BUILD CONTEXT: this Dockerfile expects to be built from the PROJECT
# ROOT (smartmail/), not from backend/, because it needs both
# backend/requirements.txt AND the trained model in ml/models/. That's
# exactly what docker-compose.yml does (context: ., dockerfile:
# backend/Dockerfile) — if building manually, run:
#   docker build -f backend/Dockerfile -t smartmail-backend .

FROM python:3.11-slim

WORKDIR /app

# Install backend dependencies first (better layer caching — this layer
# only rebuilds when requirements change, not on every code change).
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy just what the backend needs to run: its own code, plus the
# trained model + reports it loads at runtime. We deliberately do NOT
# copy ml/src, ml/data, or ml/notebooks — the backend never needs the
# training pipeline, only its output.
COPY backend/ ./backend/
COPY ml/models/ ./ml/models/

WORKDIR /app/backend

EXPOSE 8000

# Basic container healthcheck hitting the health endpoint we already built.
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/api/health')" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
