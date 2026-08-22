"""
validate_model.py
------------------
Stress-tests the trained model against deliberately ambiguous,
out-of-distribution emails — text that sits BETWEEN categories, unlike
the fairly clean, distinct templates in the training data.

WHY this instead of just trusting the 100% test-set accuracy?
    The held-out test set score (see ml/reports/evaluation.txt) mostly
    reflects that the synthetic training templates are quite distinct
    from each other, so it doesn't tell us much about how the model
    behaves on realistically ambiguous input. This script does that:
    it prints the model's confidence and runner-up category for each
    ambiguous example, which is what actually informs
    ml/reports/model_validation_report.md sections 2-4.

HOW to run:
    python ml/src/validate_model.py
"""

import sys
from pathlib import Path

# Reuse the backend's classify_email() so this test exercises the exact
# same code path the API uses, not a separate copy of the logic.
BACKEND_DIR = Path(__file__).resolve().parent.parent.parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

from app.ml.predict import classify_email  # noqa: E402

# (email text, human label describing which real-world overlap this probes)
AMBIGUOUS_CASES = [
    ("Your invoice payment is overdue, please review immediately.", "important/work overlap"),
    ("Team meeting reminder: quarterly review deadline is critical, please attend.", "work/important overlap"),
    ("Limited time offer: renew your subscription now to avoid losing access!", "promotional/spam overlap"),
    ("You have been selected for an exclusive 70% discount, claim now!", "promotional/spam overlap"),
    ("Hey, exciting news - we are having a work party this Friday, you in?", "work/personal/social overlap"),
    ("URGENT: verify your account or it will be suspended within 24 hours.", "important/spam overlap (phishing-like)"),
    ("Thanks for connecting! Check out our community meetup next week.", "social/promotional overlap"),
    ("asdf jkl random text 12345", "nonsense/out-of-distribution"),
]


def main():
    print("SmartMail — Ambiguous Input Stress Test")
    print("=" * 70)
    print("None of this text appears in the training data. It's designed to")
    print("probe category boundaries the clean synthetic templates don't.\n")

    for text, label in AMBIGUOUS_CASES:
        result = classify_email(text)
        top3 = sorted(result["all_scores"].items(), key=lambda x: -x[1])[:3]
        top3_str = ", ".join(f"{cat} {score*100:.1f}%" for cat, score in top3)

        print(f"[{label}]")
        print(f"  Text:      {text}")
        print(f"  Predicted: {result['category'].upper()} ({result['confidence']*100:.1f}%)")
        print(f"  Top 3:     {top3_str}")
        print()


if __name__ == "__main__":
    main()
