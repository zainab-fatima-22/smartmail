# SmartMail

An end-to-end machine learning application that classifies emails into
six categories using **TF-IDF and Logistic Regression** — not an LLM —
with a FastAPI backend and a React + TypeScript frontend.

**Status: Day 5 of 5 — Final Production Version** ✅

---

## Overview

SmartMail takes an email (pasted or uploaded as `.txt`/`.eml`) and
classifies it as **Spam, Promotional, Work, Personal, Important, or
Social**, returning a category, a confidence score, a plain-language
explanation, the specific words that drove the prediction, and how long
the prediction took. Every prediction is saved to a searchable history,
and a statistics dashboard summarizes classification trends over time.

This is a learning-focused portfolio project: the goal was to build and
understand a complete, real ML pipeline end-to-end — data, cleaning,
features, model, API, UI — rather than wrap an LLM in a chat box.

## Features

- Paste an email or upload a `.txt`/`.eml` file
- Category + confidence score + human-readable explanation
- **Feature-level explanation**: the actual words that pushed the model
  toward its prediction, derived from the model's own coefficients
- Low-confidence warning when the model isn't sure
- Searchable, filterable, sortable prediction history with delete
  (single item or clear-all, with confirmation)
- Statistics dashboard: totals, spam %, average confidence, category
  breakdown chart
- Responsive design (desktop, tablet, mobile)
- Loading, empty, and error states throughout
- Privacy-conscious by design (see Privacy below)

## Machine Learning Approach

SmartMail deliberately uses a **classical NLP/ML pipeline**, not an LLM:

```
Raw Email
  ->
Text Cleaning (lowercase, whitespace normalization)
  ->
Train/Test Split (80/20, stratified by category)
  ->
TF-IDF Vectorization (unigrams + bigrams)
  ->
Logistic Regression (multiclass, class_weight="balanced")
  ->
Prediction + Confidence (predict_proba)
  ->
Feature-level Explanation (coefficients x TF-IDF weights)
```

**TF-IDF**, in plain terms: a model can't read text directly, so each
email is converted into a vector of numbers — one per word in the
vocabulary. A word's score is high when it appears often in *this*
email but rarely across *all* emails (so "meeting" scores high in work
emails; "the" scores low everywhere, because it's common everywhere).

**Logistic Regression** was chosen over more complex models because
it's fast, doesn't require GPU/heavy infra, and — crucially — is
**interpretable**: its learned coefficients are what power the
"detected patterns" explanation feature, which wouldn't be
straightforward with a black-box model.

## Architecture

```
Browser (React SPA)
    |  fetch() -- JSON / multipart
    v
FastAPI backend  ------------->  SQLite (prediction_history)
    |
    v
scikit-learn Pipeline (TF-IDF + LogisticRegression)
    loaded once from ml/models/email_classifier.joblib
```

The `ml/` training pipeline and the `backend/` serving code are
intentionally decoupled: `ml/src/train.py` produces a single
`.joblib` artifact, and the backend only ever loads and calls that
artifact — it never re-trains or depends on the training scripts.

## Tech Stack

| Layer | Technology |
|---|---|
| Machine learning | Python, pandas, NumPy, scikit-learn, matplotlib, seaborn, joblib |
| Backend | FastAPI, Pydantic, SQLAlchemy, SQLite, python-dotenv |
| Frontend | React, TypeScript, Vite, recharts, lucide-react |
| Testing | pytest, Vitest, React Testing Library |
| Deployment | Docker, docker-compose, nginx |

## Dataset

Training data (`ml/data/raw/emails.csv`) is **synthetic and
template-generated** — 720 rows, 120 per category, fully documented in
`ml/data/raw/DATASET_INFO.md` (source, generation method, category
mapping, and honest limitations). No private or real individuals'
emails were used anywhere.

## ML Pipeline

See "Machine Learning Approach" above for the stage-by-stage breakdown.
Full code: `ml/src/train.py`.

## Installation

Requires Python 3.11+ and Node.js 20+ (or Docker — see below).

> **`backend/` is Python (FastAPI). `frontend/` is Node (npm/Vite).**
> `npm install` only belongs inside `frontend/` — running it inside
> `backend/` fails with `ENOENT: no such file or directory, open
> '...\backend\package.json'` because there is no `package.json` there
> by design. The backend's dependencies are installed with `pip`,
> shown below, not npm.

```bash
git clone <this-repo>
cd smartmail
pip install -r requirements.txt -r backend/requirements.txt
```

## Backend Setup

```bash
cp backend/.env.example backend/.env   # optional -- sensible defaults exist without it
cd backend
uvicorn app.main:app --reload --port 8000
```
Visit `http://localhost:8000/docs` for interactive API docs.

## Frontend Setup

```bash
cd frontend
cp .env.example .env
npm install
npm run dev
```
Visit `http://localhost:5173`.

## Running the Project

**Option A -- manually (two terminals):** backend setup above, then
frontend setup above, in that order (frontend needs the backend running
to show real data).

**Option B -- Docker (one command):**
```bash
python ml/src/train.py   # only if ml/models/email_classifier.joblib doesn't exist yet
docker compose up --build
```
Frontend: `http://localhost:5173` -- Backend: `http://localhost:8000`

## API Endpoints

Full reference: `docs/api.md`.

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | API + model status |
| POST | `/api/predict` | Classify pasted email text |
| POST | `/api/predict/upload` | Classify an uploaded `.txt`/`.eml` file |
| GET | `/api/history` | List predictions (search/filter/sort/paginate) |
| DELETE | `/api/history/{id}` | Delete one history entry |
| DELETE | `/api/history` | Clear all history |
| GET | `/api/statistics` | Dashboard summary numbers |

## Screenshots

Not included in this repository -- this project was built and verified
without a graphical environment available. Run the app locally
(`docker compose up --build` is fastest) and the Dashboard, Classify
Email, History, and Statistics pages are all a browser tab away.

## Model Performance

Full report: `ml/reports/model_validation_report.md`.

The held-out test set scores 100% accuracy/precision/recall/F1 -- this
mostly reflects that the synthetic training templates are quite
distinct from each other, and **should not be read as a real-world
accuracy claim**. More informative: a stress test against deliberately
ambiguous, out-of-distribution emails (`ml/src/validate_model.py`)
shows confidence dropping sharply (from ~95%+ down to 20-65%) exactly
where you'd expect real confusion -- **Work vs. Important** and, most
confusably, **Promotional vs. Spam** (one test case scored a near-exact
tie between the two). This is the more honest signal of how the model
actually behaves.

## Limitations

- Educational ML classifier, **not** a production email security system.
- Training data is synthetic -- see `ml/data/raw/DATASET_INFO.md`.
- Confidence is a model probability, not a certainty; categories can
  and do overlap (see Model Performance above).
- A linear model has no notion of word order or negation.
- Not evaluated against real spam corpora or adversarial/obfuscated
  spam text.
- Should be retrained if the underlying data distribution changes
  significantly.

## Privacy

- **Full email text is never stored.** Prediction history keeps only
  an 80-character preview (`backend/app/database/models.py`).
- File uploads are read into memory, classified, and discarded --
  never written to disk.
- No third-party services see your email content -- classification
  runs entirely on this server, using a local model (no LLM API calls).
- No authentication/user accounts exist yet, so history is
  shared/unscoped in this version -- see Future Improvements.

## Future Improvements

- Naive Bayes / Linear SVM comparison
- Transformer-based classification (BERT) as an alternative model
- Real-world spam datasets, adversarial/obfuscated-text evaluation
- User accounts + per-user history
- Gmail/Outlook integration via OAuth
- Attachment analysis, URL reputation checks, phishing-specific detection
- Multilingual classification
- Rate limiting on the API (not yet implemented)
- Alembic migrations instead of `create_all()` for schema changes

## Project Structure

```
smartmail/
|-- backend/            FastAPI app, SQLAlchemy models, tests
|   |-- app/
|   |   |-- api/routes/  health, prediction, upload, history, statistics
|   |   |-- ml/           model loading, preprocessing, prediction, file extraction
|   |   |-- database/     engine, ORM models, CRUD
|   |   `-- schemas/      Pydantic request/response models
|   |-- tests/            API tests + isolated database tests
|   |-- Dockerfile
|   `-- .env.example
|-- frontend/            React + TypeScript (Vite)
|   |-- src/
|   |   |-- pages/        Dashboard, ClassifyEmail, History, Statistics, About
|   |   |-- components/   Layout, CategoryBadge, Card, Confidence, States
|   |   |-- services/     api.ts (all backend calls)
|   |   |-- types/        TypeScript types mirroring backend schemas
|   |   `-- styles/        design tokens + component/page CSS
|   `-- Dockerfile
|-- ml/                  Training pipeline (independent of the backend)
|   |-- data/             raw + processed datasets, documentation
|   |-- src/               generate_dataset, load, clean, eda, train, predict, validate_model
|   |-- models/            trained email_classifier.joblib
|   |-- reports/            evaluation.txt, charts, model_validation_report.md
|   `-- tests/
|-- docs/api.md
|-- docker-compose.yml
`-- requirements.txt
```

## Testing

63 tests across the stack -- run all of them with:

```bash
pytest ml/tests/ backend/tests/ -v          # 45 Python tests
cd frontend && npm run test                  # 18 frontend tests
```

| Suite | File | Covers |
|---|---|---|
| ML pipeline | `ml/tests/test_ml.py` | cleaning, loading, prediction, long/unicode/symbol-only input, confidence sanity checks |
| API | `backend/tests/test_api.py` | all endpoints, validation, uploads, error codes |
| Database | `backend/tests/test_database.py` | CRUD in isolation (in-memory DB) -- create, search, filter, sort, paginate, delete, statistics |
| Frontend | `frontend/src/pages/__tests__/*.test.tsx` | rendering, loading/empty/error states, classify flow, uploads, low-confidence warning, history delete (incl. failure feedback) |

## Git Commit History

```
feat: build initial email classification model              (Day 1)
feat: add FastAPI prediction backend                          (Day 2)
feat: build React email classification dashboard              (Day 3)
feat: add email upload analytics and smart UI features         (Day 4)
docs: finalize SmartMail project and production setup          (Day 5)
```

This project was also debugged as a real-world exercise partway
through Day 5: a timezone bug (history timestamps displaying in the
wrong timezone due to SQLite dropping tzinfo), a search-input race
condition, and silent delete failures were found and fixed, with
regression tests added for each. See `backend/app/schemas/prediction.py`
(`ensure_utc`), `frontend/src/pages/History.tsx` (debounce + stale-response
guard + error surfacing), and their corresponding tests.

## Acceptance Criteria

- [x] Dataset exists and is documented
- [x] Data cleaning, TF-IDF, Logistic Regression all working
- [x] Model evaluated (accuracy/precision/recall/F1/confusion matrix) + validated against ambiguous inputs
- [x] Model saved via joblib, CLI prediction works
- [x] FastAPI backend: health, predict, upload, history, statistics all working
- [x] SQLite database working, tested in isolation
- [x] React frontend: classification, confidence, history, statistics, search/filter all working
- [x] File upload (.txt/.eml) working, validated
- [x] Error handling, loading states, responsive design working
- [x] 63 tests across ML/backend/frontend
- [x] `.env` protected via `.gitignore`, `.env.example` provided for both backend and frontend
- [x] Project runs locally (manual or Docker)
- [x] Git history is clean, incremental, and documented
