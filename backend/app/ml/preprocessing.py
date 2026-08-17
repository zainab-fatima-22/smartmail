"""
preprocessing.py
-----------------
Text cleaning used before running a prediction, mirroring the cleaning
done during training (ml/src/clean_data.py).

WHY duplicate this instead of importing from ml/src?
    The backend and the ml/ training code are meant to be independently
    deployable (e.g. the backend could ship in a Docker image without the
    ml/src training scripts). Keeping a small, self-contained copy avoids
    a cross-package import path headache. If this project grows, the
    cleaning logic could be extracted into a shared installable package.

    IMPORTANT: this must stay logically identical to ml/src/clean_data.py
    clean_text(), otherwise predictions could differ from what training
    expected.

WHICH file:
    backend/app/ml/preprocessing.py

HOW to test it:
    From backend/: pytest tests/ -v
"""

import re


def clean_text(text: str) -> str:
    """Normalize email text the same way training data was cleaned."""
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text
