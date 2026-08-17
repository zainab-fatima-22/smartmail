# SmartMail — AI Email Classifier

**Status: Day 2 of 5 — FastAPI Backend**

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

## What's next

- **Day 3:** React + TypeScript dashboard.
- **Day 4:** File upload, explanations, low-confidence warnings, search/filter.
- **Day 5:** Full test suite, Docker, final polished README.

## Git

```bash
git init
git add .
git commit -m "feat: build initial email classification model"
# ... Day 2:
git add .
git commit -m "feat: add FastAPI prediction backend"
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
