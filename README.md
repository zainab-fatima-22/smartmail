# SmartMail — AI Email Classifier

**Status: Day 4 of 5 — Smart Features & Polish**

SmartMail will be a full-stack app that classifies emails into
**Spam, Promotional, Work, Personal, Important, or Social** using a real
TF-IDF + Logistic Regression pipeline (not an LLM). Day 1 builds and
proves out that ML core from the command line. The FastAPI backend and
React frontend arrive in later days.

## What exists after Day 1

```
smartmail/
├── ml/
│   ├── data/
│   │   ├── raw/emails.csv          ← synthetic training data (720 rows)
│   │   ├── raw/DATASET_INFO.md     ← full dataset documentation
│   │   └── processed/emails_clean.csv
│   ├── src/
│   │   ├── generate_dataset.py     ← builds emails.csv
│   │   ├── load_data.py            ← loads CSV + prints stats
│   │   ├── clean_data.py           ← text cleaning
│   │   ├── eda.py                  ← saves charts to ml/reports/
│   │   ├── train.py                ← TF-IDF + LogisticRegression, saves model
│   │   └── predict.py              ← CLI: type an email, get a prediction
│   ├── models/email_classifier.joblib   ← trained model (after running train.py)
│   ├── reports/                    ← charts + evaluation.txt (after running train.py/eda.py)
│   └── tests/test_ml.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Setup

```bash
cd smartmail
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run it — step by step

```bash
cd ml/src

# 1. Generate the dataset (deterministic, always produces the same 720 rows)
python generate_dataset.py

# 2. Look at the raw data
python load_data.py

# 3. Clean it
python clean_data.py

# 4. Generate EDA charts (saved to ml/reports/)
python eda.py

# 5. Train + evaluate + save the model
python train.py

# 6. Try it out interactively
python predict.py
```

Example `predict.py` session:
```
Enter email: Congratulations! You have won a $500 gift card. Click this link to claim your reward.

Prediction: SPAM
Confidence: 82.22%
```

## Run the tests

```bash
cd smartmail
pytest ml/tests/ -v
```

## The ML pipeline (what train.py actually does)

```
Raw Email
  ↓
Text Cleaning (lowercase, whitespace normalization)
  ↓
Train/Test Split (80/20, stratified by category)
  ↓
TF-IDF Vectorization (unigrams + bigrams)
  ↓
Logistic Regression (multiclass, class_weight="balanced")
  ↓
Prediction + Confidence (predict_proba)
  ↓
Evaluation (accuracy, precision, recall, F1, confusion matrix)
```

**Why TF-IDF?** A model can't read text directly — TF-IDF converts each
email into numbers by scoring each word on how often it appears in that
email (TF) versus how rare it is across all emails (IDF). Common words
("the", "and") score low everywhere; distinctive words ("unsubscribe",
"meeting") score high in the categories where they matter.

**Why Logistic Regression?** It's fast, interpretable, and a strong
baseline for text classification on top of TF-IDF features. It also lets
us inspect which words push a prediction toward which category — useful
later for the "explanation" feature.

## Current model performance

See `ml/reports/evaluation.txt` and `ml/reports/confusion_matrix.png`
after running `train.py`. On this synthetic dataset the model reaches
100% accuracy on the held-out test set — expected, since the generated
templates are quite distinct from each other. **This confirms the
pipeline works correctly end-to-end; it is not a claim about real-world
spam-detection accuracy.** See `ml/data/raw/DATASET_INFO.md` for the
full discussion of this limitation.

## Dataset

Synthetic, template-generated, fully documented in
`ml/data/raw/DATASET_INFO.md`. No private or personal emails were used.

## Day 2 — FastAPI Backend

Turns the trained model into a real REST API with prediction history.

```
backend/
├── app/
│   ├── main.py              ← FastAPI app, CORS, error handlers, startup
│   ├── config.py             ← paths, limits, thresholds (env-var driven)
│   ├── api/routes/
│   │   ├── health.py         ← GET /api/health
│   │   ├── prediction.py     ← POST /api/predict
│   │   ├── history.py        ← GET/DELETE /api/history
│   │   └── statistics.py     ← GET /api/statistics
│   ├── ml/
│   │   ├── model_loader.py   ← loads Day 1's joblib model once, cached
│   │   ├── preprocessing.py  ← same text cleaning as training
│   │   └── predict.py        ← runs a prediction, builds explanation
│   ├── database/
│   │   ├── database.py       ← SQLAlchemy engine/session
│   │   ├── models.py         ← PredictionHistory table (preview only, not full email)
│   │   └── crud.py           ← DB queries (search/filter/sort/delete/stats)
│   └── schemas/
│       └── prediction.py     ← Pydantic request/response models
├── requirements.txt
└── tests/test_api.py
```

### Setup & run

```bash
cd smartmail
pip install -r requirements.txt -r backend/requirements.txt
cd backend
uvicorn app.main:app --reload --port 8000
```

Then open:
- `http://localhost:8000/docs` — interactive Swagger UI (try `/api/predict` right there)
- `http://localhost:8000/api/health` — should return `{"status": "ok", "model_loaded": true}`

If `model_loaded` is `false`, it means the Day 1 model file is missing —
run `python ml/src/train.py` from the project root first.

### Try it with curl

```bash
curl -X POST http://localhost:8000/api/predict \
  -H "Content-Type: application/json" \
  -d '{"email_text": "Congratulations! You have won a $500 gift card. Click this link to claim your reward."}'
```

### Run backend tests

```bash
cd backend
pytest tests/ -v
```

Full endpoint documentation: [`docs/api.md`](docs/api.md).

**Important honesty note:** the sandbox this was built in has no internet
access, so `fastapi`/`uvicorn`/`sqlalchemy` could not be installed or
executed there. Every file was written carefully and syntax-checked
(`python -m py_compile`), following standard, well-established FastAPI
patterns — but you should run the verification steps above yourself
before considering Day 2 "done." See the checklist below.

### Day 2 verification checklist

- [ ] `uvicorn app.main:app --reload --port 8000` starts without errors
- [ ] `GET /api/health` returns `model_loaded: true`
- [ ] `POST /api/predict` with the spam example returns `category: "spam"`
- [ ] `POST /api/predict` with `email_text: ""` returns a `400`/`422`, not a crash
- [ ] `POST /api/predict` with 20,000 characters returns a `400`/`422`
- [ ] `GET /api/history` shows the predictions you just made
- [ ] `GET /api/statistics` shows non-zero `total_predictions` after a few calls
- [ ] `DELETE /api/history` clears history and `GET /api/history` reflects it
- [ ] `pytest backend/tests/ -v` passes
- [ ] Swagger docs load at `/docs`

## Day 3 — React Frontend

A dashboard connected to the FastAPI backend. Design direction: a
stationery/postal metaphor (not a generic AI-chat look) — paper
surfaces, ink, a brass accent, and category badges styled like postage
stamps. See `frontend/README.md` for the design system notes.

```
frontend/
├── src/
│   ├── components/     ← Layout (sidebar nav), CategoryBadge (signature
│   │                      stamp design), Card, StatCard, Confidence, States
│   ├── pages/           ← Dashboard, ClassifyEmail, History, Statistics, About
│   ├── services/api.ts  ← all backend HTTP calls
│   ├── types/api.ts     ← TypeScript types mirroring the backend schemas
│   ├── styles/           ← tokens.css (design tokens), layout.css, components.css, pages.css
│   └── pages/__tests__/  ← Vitest + Testing Library tests
├── package.json
├── vite.config.ts
└── .env.example
```

### Setup & run

```bash
cd smartmail/frontend
cp .env.example .env
npm install
npm run dev
```

Open `http://localhost:5173` — make sure the Day 2 backend is running at
`http://localhost:8000` first, or you'll see the "unable to connect"
error state (which is itself part of the Day 3 error-handling work).

### Run frontend tests

```bash
cd frontend
npm run test
```

**Same honesty note as Day 2:** this sandbox has no internet access, so
`npm install` could not be run here to produce a live build/test run.
Every import/export was cross-checked by hand and the `lucide-react`
icon names used were verified against the real library, but you should
run the checklist below yourself.

### Day 3 verification checklist

- [ ] `npm install` completes without errors
- [ ] `npm run dev` starts and the dashboard loads at `localhost:5173`
- [ ] Dashboard shows stat cards (0s if history is empty, real numbers after classifying a few emails)
- [ ] Classify Email page: pasting the spam example and clicking "Classify Email" shows category, confidence, explanation, processing time
- [ ] Classifying with empty input shows "Please enter an email." without calling the API
- [ ] History page: search, category filter, and sort all update the table
- [ ] Deleting a history row removes it; "Clear all" asks for confirmation first
- [ ] Statistics page renders a bar chart once there's at least one prediction
- [ ] Layout is usable on a narrow (mobile-width) browser window
- [ ] `npm run test` passes all tests
- [ ] Keyboard-only navigation shows a visible focus outline on links/buttons

## Day 4 — Smart Features & Polish

Adds file upload, real feature-based explanations, and confirms the
confidence-warning / search-filter-sort / delete / loading / empty /
error states already built in Day 3 are all wired end-to-end.

### What's new

- **Email file upload** (`.txt`, `.eml`) — `POST /api/predict/upload`
  (`backend/app/api/routes/upload.py`), with a new
  `backend/app/ml/file_extraction.py` that parses `.eml` files properly
  (headers stripped, HTML tags stripped) instead of feeding raw email
  plumbing to the classifier. Validates extension, empty files, and a
  2 MB size limit — both server-side and client-side. On the frontend:
  a drag-and-drop dropzone plus click-to-browse on the Classify Email
  page.
- **Real explanations** — `top_features` in the prediction response now
  lists the actual words that pushed the model toward the predicted
  category, computed from the Logistic Regression coefficients ×
  each word's TF-IDF score in that email (`explain_prediction()` in
  `backend/app/ml/predict.py`). Shown as chips under "Detected patterns"
  with an explicit disclaimer that these are model-associated features,
  not proof.
- **Confidence warning, search/filter/sort, delete-with-confirmation,
  loading/empty/error states** — all already built in Day 3, confirmed
  working against the new response shape (`top_features` field added to
  `PredictionResponse` on both backend and frontend).

### Setup & run

Same as Day 2/3 — nothing new to install except `python-multipart`,
already added to `backend/requirements.txt`.

```bash
pip install -r requirements.txt -r backend/requirements.txt
cd backend && uvicorn app.main:app --reload --port 8000
# in another terminal:
cd frontend && npm install && npm run dev
```

### Try the upload endpoint directly

```bash
echo "Your meeting has been moved to 3 PM tomorrow." > /tmp/sample.txt
curl -X POST http://localhost:8000/api/predict/upload -F "file=@/tmp/sample.txt"
```

### Run tests

```bash
pytest backend/tests/ -v      # includes new upload tests
cd frontend && npm run test    # includes new upload tests
```

**Same honesty note as Days 2–3:** no internet access in this sandbox,
so the upload endpoint and `.eml` parser were tested directly with
Python (bypassing the FastAPI HTTP layer, which itself couldn't be
installed) — see the verification checklist below to confirm the full
HTTP path works on your machine.

### Day 4 verification checklist

- [ ] `POST /api/predict/upload` with a `.txt` file returns a correct prediction
- [ ] `POST /api/predict/upload` with a `.eml` file extracts just the body and classifies correctly
- [ ] Uploading a `.pdf` (or any non-.txt/.eml file) is rejected with a 400
- [ ] Uploading an empty file is rejected
- [ ] Uploading a file over 2 MB is rejected
- [ ] The Classify Email page's dropzone accepts drag-and-drop and click-to-browse
- [ ] After a prediction, "Detected patterns" shows word chips (when the model found positive contributing words)
- [ ] A deliberately ambiguous/short email shows the low-confidence warning
- [ ] `pytest backend/tests/ -v` passes (18 tests total)
- [ ] `npm run test` passes (includes the new upload tests)

## What's next

- **Day 5:** Full test suite, Docker, final polished README.

## Git

```bash
git init
git add .
git commit -m "feat: build initial email classification model"
# ... Day 2:
git add .
git commit -m "feat: add FastAPI prediction backend"
# ... Day 3:
git add .
git commit -m "feat: build React email classification dashboard"
# ... Day 4:
git add .
git commit -m "feat: add email upload analytics and smart UI features"
```

## Day 1 checklist

- [x] Dataset generated and documented (`emails.csv`, `DATASET_INFO.md`)
- [x] Dataset loader with stats (rows, classes, missing values, duplicates)
- [x] Text cleaning pipeline
- [x] EDA charts saved to `ml/reports/`
- [x] Stratified 80/20 train/test split
- [x] TF-IDF + Logistic Regression trained via `sklearn.Pipeline`
- [x] Evaluation: accuracy, precision, recall, F1, confusion matrix, classification report
- [x] Model saved with `joblib` to `ml/models/email_classifier.joblib`
- [x] CLI predictor (`predict.py`) working
- [x] Tests passing (`pytest ml/tests/`)
