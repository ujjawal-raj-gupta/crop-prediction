"""
STEP 4 — Training Script (train_model.py)

This script trains the final model for Smart Crop Advisor and saves:
- crop_model.pkl
- soil_encoder.pkl

What it does:
1) Loads data/crop_data.csv (created in Step 2)
2) Encodes soil_type using LabelEncoder
3) Splits into train/test (80/20) with stratification
4) Trains a RandomForestClassifier (best model from Step 3 evaluation)
5) Prints train accuracy, test accuracy, and a classification report
6) Saves the model + encoder using joblib
"""

from __future__ import annotations

from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from features import add_engineered_features, default_feature_cols


PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "crop_data.csv"

MODEL_PATH = PROJECT_ROOT / "crop_model.pkl"
ENCODER_PATH = PROJECT_ROOT / "soil_encoder.pkl"
FEATURE_COLS_PATH = PROJECT_ROOT / "feature_cols.pkl"


def main() -> None:
    if not DATA_PATH.exists():
        raise FileNotFoundError(
            f"Missing dataset: {DATA_PATH}\n"
            "Run Step 2 first: python prepare_data.py"
        )

    df = pd.read_csv(DATA_PATH)

    # Encode soil_type (categorical -> numeric)
    soil_encoder = LabelEncoder()
    df["soil_type_encoded"] = soil_encoder.fit_transform(df["soil_type"])

    df = add_engineered_features(df)
    feature_cols = default_feature_cols()

    X = df[feature_cols]
    y = df["label"]

    # Train/test split (reproducible + stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y,
    )

    # Final model: Random Forest (strong performance on this dataset)
    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    # Train vs test accuracy to detect overfitting/underfitting
    train_pred = model.predict(X_train)
    test_pred = model.predict(X_test)

    train_acc = accuracy_score(y_train, train_pred)
    test_acc = accuracy_score(y_test, test_pred)

    print("Train accuracy:", round(train_acc, 4))
    print("Test accuracy :", round(test_acc, 4))
    print("\nClassification report (test set):")
    print(classification_report(y_test, test_pred))

    # Save artifacts for Streamlit app
    joblib.dump(model, MODEL_PATH)
    joblib.dump(soil_encoder, ENCODER_PATH)
    joblib.dump(feature_cols, FEATURE_COLS_PATH)

    print("\nSaved model  :", MODEL_PATH)
    print("Saved encoder:", ENCODER_PATH)
    print("Saved features:", FEATURE_COLS_PATH)


if __name__ == "__main__":
    main()

