# SmartMail — AI Email Classifier

**Status: Day 1 of 5 — Machine Learning Foundation**

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

## What's next

- **Day 2:** FastAPI backend exposing `/api/predict`, `/api/history`,
  `/api/statistics` on top of this trained model, with a SQLite history
  table.
- **Day 3:** React + TypeScript dashboard.
- **Day 4:** File upload, explanations, low-confidence warnings, search/filter.
- **Day 5:** Full test suite, Docker, final polished README.

## Git

```bash
git init
git add .
git commit -m "feat: build initial email classification model"
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
