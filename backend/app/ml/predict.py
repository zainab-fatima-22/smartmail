"""
predict.py
----------
Runs a single prediction through the loaded ML pipeline and builds a
simple explanation string.

WHAT are we doing?
    1. Cleaning the input text the same way training data was cleaned.
    2. Running it through the pipeline to get a category + confidence.
    3. Building a short, honest explanation.
    4. Timing how long the prediction took.

WHY a separate function from the API route?
    Keeps api/routes/prediction.py focused on HTTP concerns (request/
    response, status codes) while this file focuses on ML concerns. This
    also makes it easy to unit-test prediction logic without spinning up
    a web server.

WHICH file:
    backend/app/ml/predict.py

HOW it connects to other files:
    - Uses model_loader.get_model() to get the trained pipeline.
    - Uses preprocessing.clean_text() to normalize input.
    - Called by api/routes/prediction.py.

NOTE on explanations (Day 2 version):
    Day 2 ships a simple, honest, category-level explanation. Day 4 adds
    a more detailed explanation using the model's learned word
    coefficients (which words pushed the prediction toward this
    category).
"""

import time

from app.ml.model_loader import get_model
from app.ml.preprocessing import clean_text

_EXPLANATIONS = {
    "spam": "The email contains promotional/scam-like language and urgency patterns commonly seen in spam.",
    "promotional": "The email contains marketing/sales language typical of promotional messages.",
    "work": "The email discusses meetings, deadlines, or work-related topics.",
    "personal": "The email has a casual, conversational tone typical of personal messages.",
    "important": "The email contains urgent or account/security-related language.",
    "social": "The email relates to social events, community activity, or social platform notifications.",
}


def classify_email(text: str) -> dict:
    """Classify a single email and return category, confidence, explanation,
    and processing time.

    Raises:
        ValueError: if the text is empty after cleaning.
    """
    start = time.perf_counter()

    cleaned = clean_text(text)
    if not cleaned:
        raise ValueError("Email text is empty after cleaning.")

    bundle = get_model()
    pipeline = bundle["pipeline"]

    probabilities = pipeline.predict_proba([cleaned])[0]
    class_order = pipeline.named_steps["classifier"].classes_
    best_idx = probabilities.argmax()
    category = str(class_order[best_idx])
    confidence = float(probabilities[best_idx])

    explanation = _EXPLANATIONS.get(category, "The model detected patterns associated with this category.")

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "category": category,
        "confidence": round(confidence, 4),
        "explanation": explanation,
        "processing_time_ms": round(elapsed_ms, 2),
        "all_scores": {
            str(cls): round(float(prob), 4) for cls, prob in zip(class_order, probabilities)
        },
    }
