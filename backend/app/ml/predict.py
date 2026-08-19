"""
predict.py
----------
Runs a single prediction through the loaded ML pipeline and builds a
simple explanation string plus a list of top contributing words.

WHAT are we doing?
    1. Cleaning the input text the same way training data was cleaned.
    2. Running it through the pipeline to get a category + confidence.
    3. Building a short, honest explanation.
    4. Finding the words that pushed the model most strongly toward the
       predicted category (Day 4 feature — see explain_prediction below).
    5. Timing how long the prediction took.

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
    - Called by api/routes/prediction.py and api/routes/upload.py.

NOTE on explanations (Day 4):
    Logistic Regression is a "linear" model: for the predicted category,
    every word in the email has a learned coefficient — a positive
    number means that word pushes the prediction TOWARD this category,
    a larger number means a stronger push. We multiply each word's
    coefficient by how present it is in this email (its TF-IDF score)
    and show the words with the biggest resulting contribution.

    THIS IS NOT PERFECT EXPLAINABLE AI. It shows which words the model
    leaned on for THIS prediction, not proof the email truly belongs to
    that category. We say so explicitly in the API response.
"""

import time

from app.config import TOP_FEATURES_COUNT
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


def explain_prediction(pipeline, cleaned_text: str, category: str, top_n: int = TOP_FEATURES_COUNT):
    """Find the words in this email that most influenced the prediction.

    For the predicted category's linear decision function, a word's
    "contribution" is its Logistic Regression coefficient for that class
    multiplied by its TF-IDF score in this specific email. Words that are
    both present in the email AND strongly associated with the category
    contribute the most.

    Returns a list of {"word": str, "weight": float} sorted by
    contribution, highest first. Only positive contributions are
    returned (words pushing TOWARD the category, not away from it).
    """
    tfidf = pipeline.named_steps["tfidf"]
    classifier = pipeline.named_steps["classifier"]

    vector = tfidf.transform([cleaned_text])  # sparse 1 x n_features
    feature_names = tfidf.get_feature_names_out()

    class_list = list(classifier.classes_)
    if category not in class_list:
        return []
    class_idx = class_list.index(category)
    coefficients = classifier.coef_[class_idx]

    nonzero_indices = vector.nonzero()[1]
    contributions = [
        (feature_names[i], float(vector[0, i] * coefficients[i])) for i in nonzero_indices
    ]
    # Keep only words that pushed TOWARD this category (positive contribution).
    contributions = [c for c in contributions if c[1] > 0]
    contributions.sort(key=lambda pair: pair[1], reverse=True)

    return [
        {"word": word, "weight": round(weight, 4)} for word, weight in contributions[:top_n]
    ]


def classify_email(text: str) -> dict:
    """Classify a single email and return category, confidence, explanation,
    top contributing words, and processing time.

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
    top_features = explain_prediction(pipeline, cleaned, category)

    elapsed_ms = (time.perf_counter() - start) * 1000

    return {
        "category": category,
        "confidence": round(confidence, 4),
        "explanation": explanation,
        "top_features": top_features,
        "processing_time_ms": round(elapsed_ms, 2),
        "all_scores": {
            str(cls): round(float(prob), 4) for cls, prob in zip(class_order, probabilities)
        },
    }

