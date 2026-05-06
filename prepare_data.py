"""
STEP 2 — Data Preparation

This script:
1) Loads the Kaggle dataset: data/Crop_recommendation.csv
2) Adds soil_type using a Bihar-inspired weighted distribution
3) Adds organic_matter based on soil_type ranges
4) Saves the final dataset to: data/crop_data.csv

Why we do this:
- The original dataset does not contain soil category information.
- For a Bihar-focused learning project, we simulate soil types and organic matter
  values using simple assumptions so we can train a model with those features too.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


PROJECT_ROOT = Path(__file__).resolve().parent
INPUT_CSV = PROJECT_ROOT / "data" / "Crop_recommendation.csv"
OUTPUT_CSV = PROJECT_ROOT / "data" / "crop_data.csv"


SOIL_TYPES = ["alluvial", "loamy", "clay", "sandy"]
# Bihar-inspired weighted distribution (assumption for this project)
SOIL_WEIGHTS = [0.70, 0.15, 0.10, 0.05]

# Organic matter (%) ranges by soil type (simulated)
ORGANIC_MATTER_RANGES: dict[str, tuple[float, float]] = {
    "sandy": (0.5, 1.5),
    "alluvial": (1.0, 3.0),
    "loamy": (1.5, 4.0),
    "clay": (2.0, 5.0),
}


def add_soil_type(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    df = df.copy()
    df["soil_type"] = rng.choice(SOIL_TYPES, size=len(df), p=SOIL_WEIGHTS)
    return df


def add_organic_matter(df: pd.DataFrame, rng: np.random.Generator) -> pd.DataFrame:
    df = df.copy()

    organic = np.empty(len(df), dtype=float)
    for soil, (low, high) in ORGANIC_MATTER_RANGES.items():
        mask = df["soil_type"] == soil
        count = int(mask.sum())
        if count == 0:
            continue
        organic[mask.to_numpy()] = rng.uniform(low, high, size=count)

    df["organic_matter"] = np.round(organic, 2)
    return df


def main() -> None:
    if not INPUT_CSV.exists():
        raise FileNotFoundError(f"Input file not found: {INPUT_CSV}")

    # Fixed seed so you get the same soil/organic_matter every run (reproducible)
    rng = np.random.default_rng(42)

    df = pd.read_csv(INPUT_CSV)
    df = add_soil_type(df, rng)
    df = add_organic_matter(df, rng)

    # Basic sanity checks
    required_cols = {
        "N",
        "P",
        "K",
        "temperature",
        "humidity",
        "ph",
        "rainfall",
        "label",
        "soil_type",
        "organic_matter",
    }
    missing = required_cols - set(df.columns)
    if missing:
        raise ValueError(f"Missing expected columns after preparation: {sorted(missing)}")

    if df[["soil_type", "organic_matter"]].isna().any().any():
        raise ValueError("Found missing values in soil_type or organic_matter.")

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)

    print("Saved:", OUTPUT_CSV)
    print("Rows, Cols:", df.shape)
    print("Soil distribution:")
    print(df["soil_type"].value_counts(normalize=True).round(3))
    print("organic_matter (min/max):", float(df["organic_matter"].min()), float(df["organic_matter"].max()))


if __name__ == "__main__":
    main()

