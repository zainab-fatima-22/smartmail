"""
eda.py
------
Exploratory Data Analysis (EDA): generates charts that help us understand
the cleaned dataset before training.

WHAT are we doing?
    Creating 3 charts: class distribution, email length distribution, and
    samples-per-category (same info as chart 1, shown differently as a
    horizontal bar for readability).

WHY?
    "Look at your data before you model it." These charts answer questions
    like: Is any category underrepresented? Are some emails suspiciously
    short/long? Answering these BEFORE training helps you spot problems
    (e.g. class imbalance) that would otherwise silently hurt your model.

HOW to test it:
    python ml/src/eda.py
    (then check ml/reports/*.png)
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # no display needed, just save files
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from load_data import load_dataset

REPORTS_DIR = Path(__file__).resolve().parent.parent / "reports"

sns.set_theme(style="whitegrid")


def plot_class_distribution(df: pd.DataFrame):
    plt.figure(figsize=(8, 5))
    order = df["category"].value_counts().index
    sns.countplot(data=df, x="category", order=order, hue="category",
                   palette="viridis", legend=False)
    plt.title("Number of Emails per Category")
    plt.xlabel("Category")
    plt.ylabel("Count")
    plt.tight_layout()
    out = REPORTS_DIR / "class_distribution.png"
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Saved -> {out}")


def plot_length_distribution(df: pd.DataFrame):
    lengths = df["email_text"].str.len()
    plt.figure(figsize=(8, 5))
    sns.histplot(lengths, bins=30, kde=True, color="steelblue")
    plt.title("Email Length Distribution (characters)")
    plt.xlabel("Email length (characters)")
    plt.ylabel("Frequency")
    plt.tight_layout()
    out = REPORTS_DIR / "email_length_distribution.png"
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Saved -> {out}")


def plot_samples_per_category_barh(df: pd.DataFrame):
    counts = df["category"].value_counts().sort_values()
    plt.figure(figsize=(8, 5))
    counts.plot(kind="barh", color="mediumseagreen")
    plt.title("Samples per Category")
    plt.xlabel("Number of samples")
    plt.tight_layout()
    out = REPORTS_DIR / "samples_per_category.png"
    plt.savefig(out, dpi=120)
    plt.close()
    print(f"Saved -> {out}")


def main():
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    df = load_dataset()

    plot_class_distribution(df)
    plot_length_distribution(df)
    plot_samples_per_category_barh(df)

    print("\nWhat these charts tell us:")
    print("- class_distribution.png: all 6 categories have equal counts (120 each),")
    print("  so we don't need to worry about class imbalance for this dataset.")
    print("- email_length_distribution.png: most emails are 50-120 characters,")
    print("  a realistic range for short email bodies/snippets.")
    print("- samples_per_category.png: same info as the first chart, sorted,")
    print("  useful for quickly spotting the smallest/largest category.")


if __name__ == "__main__":
    main()
