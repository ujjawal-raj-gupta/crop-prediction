"""
Quick evaluation script for Step 3.

Runs the same train/test split and compares 4 models:
- Logistic Regression
- Decision Tree
- Random Forest
- Gradient Boosting

Prints train accuracy, test accuracy, and the gap (train - test)
to help detect underfitting/overfitting.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

from features import add_engineered_features, default_feature_cols


def main() -> None:
    project_root = Path(__file__).resolve().parent
    data_path = project_root / "data" / "crop_data.csv"

    df = pd.read_csv(data_path)

    soil_encoder = LabelEncoder()
    df["soil_type_encoded"] = soil_encoder.fit_transform(df["soil_type"])

    df = add_engineered_features(df)
    feature_cols = default_feature_cols()

    X = df[feature_cols]
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    models = {
        "LogisticRegression": LogisticRegression(max_iter=3000),
        "DecisionTree": DecisionTreeClassifier(random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingClassifier(random_state=42),
    }

    rows: list[tuple[str, float, float, float]] = []
    for name, model in models.items():
        model.fit(X_train, y_train)
        train_acc = accuracy_score(y_train, model.predict(X_train))
        test_acc = accuracy_score(y_test, model.predict(X_test))
        gap = train_acc - test_acc
        rows.append((name, train_acc, test_acc, gap))

    rows.sort(key=lambda t: t[2], reverse=True)  # sort by test accuracy

    print("Model results (sorted by test accuracy):")
    for name, train_acc, test_acc, gap in rows:
        print(f"- {name:18s}  train={train_acc:.4f}  test={test_acc:.4f}  gap={gap:.4f}")

    best_name, best_train, best_test, best_gap = rows[0]
    print("\nBest by test accuracy:")
    print(f"- model={best_name}  train={best_train:.4f}  test={best_test:.4f}  gap={best_gap:.4f}")


if __name__ == "__main__":
    main()

