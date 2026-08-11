"""
predict.py
----------
Command-line tool to classify a single email using the trained model.

WHAT are we doing?
    Loading the saved model from disk and using it to predict a category
    (plus a confidence score) for text you type in.

WHY a separate file from train.py?
    In a real application you train ONCE (or occasionally, when you have
    new data) but predict MANY times. Separating them means the backend
    (Day 2) can reuse this same loading/prediction logic without
    retraining the model on every request.

HOW does it connect to other files?
    - Loads ml/models/email_classifier.joblib, produced by train.py.
    - Day 2's backend/app/ml/predict.py will follow this same pattern.

HOW to test it:
    python ml/src/predict.py
    (then type an email when prompted)
"""

from pathlib import Path

import joblib

MODEL_PATH = Path(__file__).resolve().parent.parent / "models" / "email_classifier.joblib"


def load_model(path: Path = MODEL_PATH):
    if not path.exists():
        raise FileNotFoundError(
            f"No trained model found at {path}. Run 'python ml/src/train.py' first."
        )
    bundle = joblib.load(path)
    return bundle["pipeline"], bundle["labels"]


def predict_email(text: str, pipeline, labels) -> dict:
    """Predict category + confidence for a single email string.

    WHY predict_proba instead of just predict?
        predict() only gives us the winning class. predict_proba() gives
        us a probability for EVERY class, which lets us report a
        confidence score (how sure the model is) instead of just a raw
        label. This is what SmartMail shows to the user, and it's also
        what later lets us flag "low confidence" predictions.
    """
    probabilities = pipeline.predict_proba([text])[0]
    class_order = pipeline.named_steps["classifier"].classes_
    best_idx = probabilities.argmax()
    category = class_order[best_idx]
    confidence = probabilities[best_idx]

    all_scores = {
        cls: float(prob) for cls, prob in zip(class_order, probabilities)
    }

    return {
        "category": category,
        "confidence": float(confidence),
        "all_scores": all_scores,
    }


def main():
    pipeline, labels = load_model()
    print("SmartMail — Manual Email Classifier (Day 1 CLI)")
    print(f"Loaded model with categories: {labels}")
    print("Type an email and press Enter (or 'quit' to exit).\n")

    while True:
        text = input("Enter email: ").strip()
        if text.lower() in {"quit", "exit"}:
            print("Goodbye!")
            break
        if not text:
            print("Please enter some text.\n")
            continue

        result = predict_email(text, pipeline, labels)
        print(f"\nPrediction: {result['category'].upper()}")
        print(f"Confidence: {result['confidence'] * 100:.2f}%")
        print("All category scores:")
        for cls, score in sorted(result["all_scores"].items(), key=lambda x: -x[1]):
            print(f"  {cls:12s} {score * 100:5.2f}%")
        print()


if __name__ == "__main__":
    main()
