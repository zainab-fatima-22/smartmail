"""
test_ml.py
----------
Basic pytest tests for the Day 1 ML pipeline.

Run with:
    cd smartmail
    pytest ml/tests/ -v
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from clean_data import clean_text, clean_dataframe  # noqa: E402
from load_data import load_dataset  # noqa: E402
from predict import load_model, predict_email  # noqa: E402


def test_clean_text_lowercases():
    assert clean_text("HELLO World") == "hello world"


def test_clean_text_collapses_whitespace():
    assert clean_text("hello   \n\n  world") == "hello world"


def test_clean_text_handles_non_string():
    assert clean_text(None) == ""


def test_clean_dataframe_drops_missing_and_duplicates():
    df = pd.DataFrame(
        {
            "email_text": ["Hello there", "Hello there", None, "Meeting at 3pm"],
            "category": ["personal", "personal", "work", "work"],
        }
    )
    cleaned = clean_dataframe(df)
    assert len(cleaned) == 2  # one duplicate + one missing row removed
    assert cleaned["email_text"].is_unique


def test_dataset_loads_and_has_six_categories():
    df = load_dataset()
    assert len(df) > 0
    assert df["category"].nunique() == 6
    assert set(df.columns) == {"email_text", "category"}


def test_model_loads():
    pipeline, labels = load_model()
    assert len(labels) == 6


def test_predict_returns_valid_structure():
    pipeline, labels = load_model()
    result = predict_email("Congratulations, you won a free prize!", pipeline, labels)
    assert "category" in result
    assert "confidence" in result
    assert result["category"] in labels
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_spam_example():
    pipeline, labels = load_model()
    result = predict_email(
        "Congratulations! You have won a $500 gift card. Click this link to claim your reward.",
        pipeline,
        labels,
    )
    assert result["category"] == "spam"


def test_predict_work_example():
    pipeline, labels = load_model()
    result = predict_email("Your meeting has been moved to 3 PM tomorrow.", pipeline, labels)
    assert result["category"] == "work"


# --- Day 5: edge cases (long input, unusual text, low confidence) --------

def test_predict_handles_very_long_input_without_crashing():
    pipeline, labels = load_model()
    long_email = "Meeting reminder. " * 2000  # ~38,000 characters
    result = predict_email(long_email, pipeline, labels)
    assert result["category"] in labels
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_handles_unusual_unicode_text_without_crashing():
    pipeline, labels = load_model()
    # Emoji, non-Latin scripts, and mixed symbols — text the training
    # data never saw. The model shouldn't crash; a low-confidence,
    # plausible-ish guess is an acceptable outcome for unseen input.
    unusual_email = "会議は3時です 🎉🎉🎉 !!!¿¿¿ こんにちは"
    result = predict_email(unusual_email, pipeline, labels)
    assert result["category"] in labels
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_handles_numeric_and_symbol_only_text():
    pipeline, labels = load_model()
    result = predict_email("12345 !@#$% 67890 &*()", pipeline, labels)
    assert result["category"] in labels
    assert 0.0 <= result["confidence"] <= 1.0


def test_predict_ambiguous_text_produces_lower_confidence_than_clear_spam():
    # This is not a strict correctness requirement, but it's a useful
    # sanity check: text engineered to be ambiguous between categories
    # should not be MORE confident than an unambiguous, obvious example.
    pipeline, labels = load_model()

    clear_spam = predict_email(
        "Congratulations! You have won a $500 gift card. Click this link to claim your reward.",
        pipeline,
        labels,
    )
    ambiguous = predict_email(
        "Limited time offer: renew your subscription now to avoid losing access!",
        pipeline,
        labels,
    )
    assert ambiguous["confidence"] < clear_spam["confidence"]


def test_clean_text_handles_long_whitespace_heavy_input():
    padded = "hello" + (" " * 5000) + "world"
    result = clean_text(padded)
    assert result == "hello world"


def test_clean_text_preserves_currency_and_punctuation():
    # These aren't stripped on purpose — see clean_data.py's docstring on
    # why punctuation like "$" and "!" is kept as a useful signal.
    assert "$500" in clean_text("You won $500!!!")
    assert "!" in clean_text("You won $500!!!")
