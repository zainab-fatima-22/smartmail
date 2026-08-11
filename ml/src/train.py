"""
train.py
--------
The main training script. Run this to build the SmartMail classifier
from scratch.

WHAT are we doing?
    1. Loading and cleaning the dataset.
    2. Splitting it into training data (used to teach the model) and
       test data (used to check how well it learned, on emails it has
       never seen).
    3. Converting email text into numbers using TF-IDF.
    4. Training a Logistic Regression model on those numbers.
    5. Evaluating the model on the test set.
    6. Saving the trained model to disk so predict.py / the backend can
       reuse it without retraining.

WHY a Pipeline?
    scikit-learn's Pipeline bundles the TF-IDF step and the classifier
    step into ONE object. This matters because:
    - We can call .fit() and .predict() once instead of juggling two
      objects and remembering to apply the same vectorizer both times.
    - It PREVENTS DATA LEAKAGE: the vectorizer only learns its vocabulary
      from the training data, never the test data, because Pipeline
      handles fit/transform in the correct order automatically.

BEGINNER NOTES — what is TF-IDF?
    A model can't read words directly, it needs numbers. TF-IDF converts
    each email into a vector of numbers, one per word in the vocabulary.

    - TF (Term Frequency): how often a word appears in THIS email.
      A word that appears 3 times in a short email is probably important
      to that email's meaning.
    - IDF (Inverse Document Frequency): how RARE a word is across ALL
      emails. Common words like "the" or "and" appear everywhere, so they
      get a low IDF score (not useful for telling categories apart).
      Rare, distinctive words like "unsubscribe" or "invoice" get a high
      IDF score, because their presence is a strong signal.
    - TF-IDF = TF * IDF. It rewards words that appear often in one email
      but rarely across the whole dataset — exactly the kind of word that
      helps distinguish "spam" from "work".

    Example: the word "meeting" might get a HIGH TF-IDF score in a work
    email (appears often there, rarely in spam/social emails), while the
    word "the" gets a LOW score everywhere because it's common in all
    categories and therefore not distinctive.

WHY Logistic Regression?
    - It's fast, interpretable (we can inspect which words push a
      prediction toward which category — used later for "explanations"),
      and works very well on top of TF-IDF features for text
      classification. It's a standard, reliable baseline before trying
      anything fancier.
    - "Multiclass" here means the model chooses 1 of 6 categories, not
      just yes/no. scikit-learn handles this automatically for
      LogisticRegression using a technique that fits one decision
      boundary per class and picks the class with the highest score.

HOW to run:
    python ml/src/train.py

WHAT you'll get:
    - Console output with dataset stats, training info, and evaluation
      metrics (accuracy, precision, recall, F1, confusion matrix).
    - ml/models/email_classifier.joblib (the saved trained pipeline)
    - ml/reports/evaluation.txt (evaluation report saved to disk)
    - ml/reports/confusion_matrix.png
"""

from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    ConfusionMatrixDisplay,
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer

from load_data import load_dataset
from clean_data import clean_dataframe

BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "email_classifier.joblib"
REPORT_PATH = BASE_DIR / "reports" / "evaluation.txt"
CONFUSION_MATRIX_PATH = BASE_DIR / "reports" / "confusion_matrix.png"

RANDOM_STATE = 42


def build_pipeline() -> Pipeline:
    """Build the TF-IDF + Logistic Regression pipeline.

    We keep the parameters simple and well-reasoned rather than blindly
    tuning them:
      - ngram_range=(1, 2): looks at single words AND 2-word phrases
        (e.g. "free prize"), which captures more context than single
        words alone.
      - min_df=2: ignore words that appear in only 1 email (too rare to
        be a reliable signal, and helps avoid overfitting to noise).
      - stop_words="english": drop very common English words ("the",
        "is", "and"...) that carry little category-distinguishing signal.
      - max_iter=1000 on LogisticRegression: gives the optimizer enough
        iterations to converge on this dataset size.
      - class_weight="balanced": in case classes are ever imbalanced in
        future data, this keeps the model from favoring the majority
        class.
    """
    return Pipeline(
        steps=[
            (
                "tfidf",
                TfidfVectorizer(
                    ngram_range=(1, 2),
                    min_df=2,
                    stop_words="english",
                ),
            ),
            (
                "classifier",
                LogisticRegression(
                    max_iter=1000,
                    class_weight="balanced",
                    random_state=RANDOM_STATE,
                ),
            ),
        ]
    )


def train_and_evaluate():
    print("\nSTEP 1 — Loading and cleaning dataset")
    print("-" * 60)
    df = clean_dataframe(load_dataset())

    X = df["email_text"]
    y = df["category"]

    print("\nSTEP 2 — Train/test split")
    print("-" * 60)
    # WHY stratify=y? Stratification makes sure the train and test sets
    # both have the SAME proportion of each category as the full dataset.
    # Without it, a random split could (by bad luck) put almost no
    # "personal" emails in the test set, making that category's test
    # metrics meaningless.
    #
    # WHY does data leakage matter? If information from the test set
    # leaks into training (e.g. fitting TF-IDF on the full dataset before
    # splitting), the model gets an unfair sneak-peek at test data,
    # making evaluation metrics look better than the model actually is
    # on genuinely unseen emails. Our Pipeline avoids this because
    # .fit() is only ever called on X_train.
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=RANDOM_STATE, stratify=y
    )
    print(f"Training samples: {len(X_train)}")
    print(f"Testing samples:  {len(X_test)}")
    print("Train class distribution:")
    print(y_train.value_counts())
    print("Test class distribution:")
    print(y_test.value_counts())

    print("\nSTEP 3 — Building and training the pipeline (TF-IDF + Logistic Regression)")
    print("-" * 60)
    pipeline = build_pipeline()
    pipeline.fit(X_train, y_train)
    print("Training complete.")
    vocab_size = len(pipeline.named_steps["tfidf"].vocabulary_)
    print(f"TF-IDF vocabulary size: {vocab_size} terms")

    print("\nSTEP 4 — Evaluating on the held-out test set")
    print("-" * 60)
    y_pred = pipeline.predict(X_test)

    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average="macro", zero_division=0)
    recall = recall_score(y_test, y_pred, average="macro", zero_division=0)
    f1 = f1_score(y_test, y_pred, average="macro", zero_division=0)

    print(f"Accuracy:  {accuracy:.4f}")
    print(f"Precision (macro): {precision:.4f}")
    print(f"Recall (macro):    {recall:.4f}")
    print(f"F1-score (macro):  {f1:.4f}")

    print("\nWHY isn't accuracy alone enough?")
    print("Accuracy can be misleading with imbalanced classes: a model that")
    print("always predicts the majority class can still score high accuracy")
    print("while being useless for minority classes. Precision tells us how")
    print("many predicted-X emails were really X (false positive control).")
    print("Recall tells us how many actual-X emails the model found (false")
    print("negative control). F1 balances the two. We use 'macro' averaging")
    print("so every category counts equally, regardless of its size.")

    report = classification_report(y_test, y_pred, zero_division=0)
    print("\nClassification report:")
    print(report)

    labels = sorted(y.unique())
    cm = confusion_matrix(y_test, y_pred, labels=labels)
    print("Confusion matrix (rows = actual, columns = predicted):")
    print(labels)
    print(cm)

    # Save confusion matrix as an image
    fig, ax = plt.subplots(figsize=(7, 6))
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=labels)
    disp.plot(ax=ax, cmap="Blues", colorbar=False, xticks_rotation=45)
    plt.title("Confusion Matrix — SmartMail Classifier")
    plt.tight_layout()
    CONFUSION_MATRIX_PATH.parent.mkdir(parents=True, exist_ok=True)
    plt.savefig(CONFUSION_MATRIX_PATH, dpi=120)
    plt.close()
    print(f"\nSaved confusion matrix image -> {CONFUSION_MATRIX_PATH}")

    # Save a text evaluation report
    with open(REPORT_PATH, "w") as f:
        f.write("SmartMail — Model Evaluation Report\n")
        f.write("=" * 50 + "\n")
        f.write(f"Training samples: {len(X_train)}\n")
        f.write(f"Testing samples:  {len(X_test)}\n")
        f.write(f"TF-IDF vocabulary size: {vocab_size}\n\n")
        f.write(f"Accuracy:  {accuracy:.4f}\n")
        f.write(f"Precision (macro): {precision:.4f}\n")
        f.write(f"Recall (macro):    {recall:.4f}\n")
        f.write(f"F1-score (macro):  {f1:.4f}\n\n")
        f.write("Classification report:\n")
        f.write(report + "\n")
        f.write("Confusion matrix (rows = actual, columns = predicted):\n")
        f.write(f"Labels: {labels}\n")
        f.write(str(cm) + "\n")
    print(f"Saved evaluation report -> {REPORT_PATH}")

    print("\nSTEP 5 — Saving the trained model")
    print("-" * 60)
    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(
        {
            "pipeline": pipeline,
            "labels": labels,
            "random_state": RANDOM_STATE,
        },
        MODEL_PATH,
    )
    print(f"Saved trained model -> {MODEL_PATH}")

    return pipeline


if __name__ == "__main__":
    train_and_evaluate()
