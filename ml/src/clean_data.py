"""
clean_data.py
-------------
Cleans the raw email text before it goes into the ML pipeline, and saves
the cleaned dataset to ml/data/processed/emails_clean.csv.

WHAT are we doing?
    Normalizing raw email text: lowercasing, collapsing extra whitespace,
    dropping missing/duplicate rows.

WHY?
    Machine learning models don't understand "Meeting" and "meeting" as
    the same word unless we normalize case. Real-world text also has
    inconsistent spacing (extra newlines, tabs) that adds noise without
    adding meaning.

    IMPORTANT: we deliberately KEEP most punctuation (like "!" and "$").
    Punctuation carries real signal for this task — spam emails use "!"
    and "$" far more than work emails do. Stripping all punctuation would
    throw away a useful feature, so we only remove characters that are
    pure noise (extra whitespace, control characters).

HOW does it connect to other files?
    - Imports `load_dataset()` from load_data.py.
    - train.py imports `clean_dataframe()` from this file before
      splitting the data into train/test sets.

HOW to test it:
    python ml/src/clean_data.py
"""

import re
from pathlib import Path

import pandas as pd

from load_data import load_dataset, print_dataset_stats

PROCESSED_PATH = (
    Path(__file__).resolve().parent.parent / "data" / "processed" / "emails_clean.csv"
)


def clean_text(text: str) -> str:
    """Normalize a single email string.

    Steps:
      1. Lowercase the text (so "Free" and "free" are treated the same).
      2. Collapse repeated whitespace/newlines into a single space.
      3. Strip leading/trailing whitespace.

    We intentionally do NOT strip punctuation or numbers — words like
    "$500" or "!!!" are meaningful signals for spam detection.
    """
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    return text


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Apply full cleaning pipeline to the dataset."""
    df = df.copy()

    # 1. Drop rows with missing text or category
    before = len(df)
    df = df.dropna(subset=["email_text", "category"])
    dropped_missing = before - len(df)

    # 2. Normalize text
    df["email_text"] = df["email_text"].apply(clean_text)

    # 3. Drop empty strings after cleaning
    before = len(df)
    df = df[df["email_text"].str.len() > 0]
    dropped_empty = before - len(df)

    # 4. Normalize category labels (lowercase, stripped)
    df["category"] = df["category"].str.lower().str.strip()

    # 5. Drop duplicate emails (keep first occurrence)
    before = len(df)
    df = df.drop_duplicates(subset=["email_text"])
    dropped_dupes = before - len(df)

    df = df.reset_index(drop=True)

    print(f"Dropped {dropped_missing} rows with missing values")
    print(f"Dropped {dropped_empty} rows that were empty after cleaning")
    print(f"Dropped {dropped_dupes} duplicate rows")
    print(f"Final cleaned dataset size: {len(df)} rows")

    return df


def main():
    raw_df = load_dataset()
    print("BEFORE cleaning:")
    print_dataset_stats(raw_df)

    clean_df = clean_dataframe(raw_df)

    PROCESSED_PATH.parent.mkdir(parents=True, exist_ok=True)
    clean_df.to_csv(PROCESSED_PATH, index=False)
    print(f"\nSaved cleaned dataset -> {PROCESSED_PATH}")

    print("\nAFTER cleaning:")
    print_dataset_stats(clean_df)


if __name__ == "__main__":
    main()
