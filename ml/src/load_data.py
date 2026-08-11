"""
load_data.py
------------
Loads ml/data/raw/emails.csv and prints basic statistics about it.

WHAT are we doing?
    Reading the raw CSV into a pandas DataFrame and checking its shape,
    class balance, and data quality (missing values, duplicates).

WHY?
    Before training any model, you must understand your data. A model
    trained on a broken or wildly imbalanced dataset will behave badly,
    and you won't know why unless you looked at the data first.

HOW does it connect to other files?
    - clean_data.py imports `load_dataset()` from this file.
    - train.py calls clean_data.py's cleaning pipeline, which starts here.

HOW to test it:
    python ml/src/load_data.py
"""

from pathlib import Path
import pandas as pd

RAW_PATH = Path(__file__).resolve().parent.parent / "data" / "raw" / "emails.csv"


def load_dataset(path: Path = RAW_PATH) -> pd.DataFrame:
    """Load the raw email dataset into a pandas DataFrame."""
    if not path.exists():
        raise FileNotFoundError(
            f"Dataset not found at {path}. Run 'python ml/src/generate_dataset.py' first."
        )
    df = pd.read_csv(path)
    return df


def print_dataset_stats(df: pd.DataFrame) -> None:
    print("=" * 60)
    print("DATASET STATISTICS")
    print("=" * 60)
    print(f"Number of rows:    {len(df)}")
    print(f"Number of columns: {df.shape[1]}")
    print(f"Columns:           {list(df.columns)}")

    print(f"\nNumber of classes: {df['category'].nunique()}")
    print("\nClass distribution:")
    print(df["category"].value_counts())

    print("\nMissing values per column:")
    print(df.isnull().sum())

    n_dupes = df.duplicated(subset=["email_text"]).sum()
    print(f"\nDuplicate email_text rows: {n_dupes}")

    lengths = df["email_text"].str.len()
    print("\nEmail length (characters) stats:")
    print(f"  min: {lengths.min()}  max: {lengths.max()}  mean: {lengths.mean():.1f}")
    print("=" * 60)


if __name__ == "__main__":
    dataset = load_dataset()
    print_dataset_stats(dataset)
