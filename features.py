from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class FeatureConfig:
    eps: float = 1e-6


def add_engineered_features(df: pd.DataFrame, cfg: FeatureConfig | None = None) -> pd.DataFrame:
    """
    Add derived agronomy features used by both training and inference.

    Expects at least:
      N, P, K, temperature, humidity, ph, rainfall, soil_type_encoded, organic_matter
    """
    cfg = cfg or FeatureConfig()
    out = df.copy()
    eps = cfg.eps

    # Nutrient interactions
    out["npk_sum"] = out["N"] + out["P"] + out["K"]
    out["np_ratio"] = out["N"] / (out["P"] + eps)
    out["nk_ratio"] = out["N"] / (out["K"] + eps)
    out["pk_ratio"] = out["P"] / (out["K"] + eps)
    out["npk_balance_std"] = out[["N", "P", "K"]].std(axis=1)

    # Nutrient dominance metrics
    # - dominant nutrient: 0=N, 1=P, 2=K
    # - dominance ratio: max(N,P,K) / sum(N,P,K)
    npk = out[["N", "P", "K"]].to_numpy(dtype=float)
    out["npk_dominant_idx"] = np.argmax(npk, axis=1).astype(int)
    out["npk_dominance_ratio"] = (np.max(npk, axis=1) / (np.sum(npk, axis=1) + eps)).astype(float)

    # Weather/soil transforms
    out["rainfall_log"] = np.log1p(out["rainfall"])
    out["ph_distance_from_7"] = (out["ph"] - 7.0).abs()
    out["temp_x_humidity"] = out["temperature"] * out["humidity"]

    # Moisture / stress indices (simple, effective for trees)
    out["moisture_index"] = out["rainfall"] * (out["humidity"] / 100.0)
    out["rainfall_per_temp"] = out["rainfall"] / (out["temperature"] + eps)
    out["humidity_x_rainfall"] = out["humidity"] * out["rainfall"]

    # pH class: 0=acidic, 1=neutral, 2=alkaline (broad agronomy buckets)
    out["ph_class"] = pd.cut(
        out["ph"],
        bins=[-np.inf, 6.5, 7.5, np.inf],
        labels=[0, 1, 2],
        include_lowest=True,
    ).astype(int)

    # Simple season heuristic (Bihar-ish): 0=kharif, 1=rabi, 2=zaid
    # This is a derived proxy from rainfall+temperature (since month isn't present).
    kharif = (out["rainfall"] >= 150) & (out["temperature"] >= 23)
    rabi = (out["temperature"] < 23) & (out["rainfall"] < 150)
    out["season_idx"] = np.select([kharif, rabi], [0, 1], default=2).astype(int)

    return out


def default_feature_cols() -> list[str]:
    """
    Canonical feature order used by training & inference.
    Save this list as feature_cols.pkl after training and use it at inference time.
    """
    return [
        "N",
        "P",
        "K",
        "npk_sum",
        "np_ratio",
        "nk_ratio",
        "pk_ratio",
        "npk_balance_std",
        "npk_dominant_idx",
        "npk_dominance_ratio",
        "temperature",
        "humidity",
        "temp_x_humidity",
        "moisture_index",
        "rainfall",
        "rainfall_log",
        "rainfall_per_temp",
        "humidity_x_rainfall",
        "ph",
        "ph_distance_from_7",
        "ph_class",
        "season_idx",
        "soil_type_encoded",
        "organic_matter",
    ]


def build_model_input_row(
    *,
    n: int,
    p: int,
    k: int,
    temperature: float,
    humidity: float,
    ph: float,
    rainfall: float,
    soil_type_encoded: int,
    organic_matter: float,
    feature_cols: list[str],
) -> pd.DataFrame:
    base = pd.DataFrame(
        [
            {
                "N": n,
                "P": p,
                "K": k,
                "temperature": temperature,
                "humidity": humidity,
                "ph": ph,
                "rainfall": rainfall,
                "soil_type_encoded": soil_type_encoded,
                "organic_matter": organic_matter,
            }
        ]
    )
    full = add_engineered_features(base)

    # Ensure all expected columns exist (future-proof)
    for col in feature_cols:
        if col not in full.columns:
            full[col] = 0

    return full[feature_cols]

