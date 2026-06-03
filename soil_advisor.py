"""
Soil upgrade advisor (shared logic).

Finds high-value crops the farmer's soil is *almost* suitable for - blocked by
exactly one controllable factor (Nitrogen, Phosphorus, Potassium, or pH) - and
suggests the concrete amendment to add so the soil becomes suitable.

Design notes:
- Suitability here is about SOIL CHEMISTRY (N, P, K, pH) - the things a farmer can
  actually change. Climate (temperature/humidity/rainfall) is regional and fixed,
  and a single live weather reading is not representative of a growing season, so it
  is intentionally NOT used to gate suggestions.
- A crop qualifies when ALL controllable params are in range except exactly one,
  and that one is short (deficient) within a tolerance band ("almost" there).
- Candidates are ranked by a market value score combining demand level + price.

This module depends only on pandas/numpy + CSV paths so it can be reused by both
the Flask app (web_app.py) and the FastAPI platform.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path

import numpy as np
import pandas as pd


# Controllable soil chemistry params the farmer can amend.
CONTROLLABLE = ("N", "P", "K", "ph")

DEMAND_WEIGHT = {"high": 1.0, "medium": 0.6, "low": 0.3}

# Realistic agronomic bounds (derived from the training dataset's full range,
# with a small buffer). Inputs outside these are physically implausible for
# Indian field soils and must be rejected instead of silently scored.
REALISTIC_BOUNDS = {
    "N":  (0.0, 155.0),    # kg/ha; dataset max ~140
    "P":  (0.0, 155.0),    # kg/ha; dataset max ~145
    "K":  (0.0, 215.0),    # kg/ha; dataset max ~205
    "ph": (3.0, 10.0),     # dataset range ~3.5-9.9
}
# Climate params (cannot be amended, but useful for ranking by season/region).
CLIMATE_PARAMS = ("temperature", "humidity", "rainfall")

# Minimum sigma per param so the bell-curve score stays smooth even if a crop's
# sample std is unusually small.
_SIGMA_FLOOR = {
    "N": 5.0, "P": 5.0, "K": 5.0, "ph": 0.3,
    "temperature": 2.0, "humidity": 5.0, "rainfall": 20.0,
}

# Map dataset labels / common spellings to the market CSV crop names.
CROP_ALIASES = {
    "lentils": "lentil",
    "pigeonpea": "pigeonpeas",
    "mothbean": "mothbeans",
    "kidneybean": "kidneybeans",
    "mungbeans": "mungbean",
    "blackgrams": "blackgram",
}


def _norm(name: str) -> str:
    key = str(name).strip().lower()
    return CROP_ALIASES.get(key, key)


@dataclass
class CropProfile:
    crop: str
    ranges: dict  # param -> (lo, hi)


@dataclass
class UpgradeSuggestion:
    crop: str
    market_score: float
    demand_level: str
    price_per_kg: str
    blocking_param: str
    current_value: float
    target_value: float
    gap: float
    action_text: str


def load_crop_profiles(data_csv: str | Path) -> dict[str, CropProfile]:
    """
    Build per-crop acceptable ranges from the training dataset.

    Controllable params use the 10th-90th percentile band (the crop's typical range).
    """
    df = pd.read_csv(data_csv)
    if "label" not in df.columns:
        return {}

    profiles: dict[str, CropProfile] = {}
    for label, group in df.groupby("label"):
        ranges: dict[str, tuple[float, float]] = {}
        for param in CONTROLLABLE:
            if param in group.columns:
                lo = float(np.percentile(group[param], 10))
                hi = float(np.percentile(group[param], 90))
                ranges[param] = (lo, hi)
        profiles[_norm(label)] = CropProfile(crop=str(label), ranges=ranges)
    return profiles


def market_value_score(market_csv: str | Path) -> dict[str, dict]:
    """
    Return normalized crop -> {score, demand_level, price_per_kg}.

    Score blends demand level (60%) and price-per-kg normalized to its max (40%),
    so a crop needs both decent demand and a decent price to rank highly.
    """
    if not Path(market_csv).exists():
        return {}
    df = pd.read_csv(market_csv)
    if "crop" not in df.columns:
        return {}

    prices = pd.to_numeric(df.get("price_per_kg"), errors="coerce")
    max_price = float(prices.max()) if prices.notna().any() else 0.0

    out: dict[str, dict] = {}
    for _, row in df.iterrows():
        crop = _norm(row["crop"])
        demand = str(row.get("demand_level", "")).strip().lower()
        demand_w = DEMAND_WEIGHT.get(demand, 0.3)
        try:
            price = float(row.get("price_per_kg"))
        except (TypeError, ValueError):
            price = 0.0
        price_norm = (price / max_price) if max_price > 0 else 0.0
        score = round(0.6 * demand_w + 0.4 * price_norm, 4)
        out[crop] = {
            "score": score,
            "demand_level": str(row.get("demand_level", "")).strip(),
            "price_per_kg": str(row.get("price_per_kg", "")).strip(),
        }
    return out


def load_market_info(market_csv: str | Path) -> dict[str, dict]:
    """
    Return normalized crop -> selling info: where and to whom to sell, plus price
    and demand. Used to tell farmers where to sell each recommended crop.
    """
    if not Path(market_csv).exists():
        return {}
    df = pd.read_csv(market_csv)
    if "crop" not in df.columns:
        return {}

    out: dict[str, dict] = {}
    for _, row in df.iterrows():
        crop = _norm(row["crop"])
        out[crop] = {
            "demand_level": str(row.get("demand_level", "")).strip(),
            "price_per_kg": str(row.get("price_per_kg", "")).strip(),
            "buyer_type": str(row.get("buyer_type", "")).strip(),
            "buyer_location": str(row.get("buyer_location", "")).strip(),
        }
    return out


def amendment_for(param: str, direction: str, target: float) -> str:
    """
    Human-readable action for fixing one short/off parameter.
    direction: "below" (value under range) or "above" (value over range).
    """
    if param == "N" and direction == "below":
        return f"Add Nitrogen (urea or DAP) to raise N to about {round(target)}."
    if param == "P" and direction == "below":
        return f"Add Phosphorus (DAP or single super phosphate) to raise P to about {round(target)}."
    if param == "K" and direction == "below":
        return f"Add Potassium (muriate of potash / potash) to raise K to about {round(target)}."
    if param == "ph" and direction == "below":
        return f"Soil is too acidic - add agricultural lime to raise pH to about {round(target, 1)}."
    if param == "ph" and direction == "above":
        return (
            f"Soil is too alkaline - add gypsum, elemental sulphur, or organic matter "
            f"to lower pH to about {round(target, 1)}."
        )
    return f"Adjust {param} toward about {round(target, 2)}."


def _is_fixable(param: str, direction: str) -> bool:
    """N/P/K are practically fixable only when deficient; pH both directions."""
    if param == "ph":
        return True
    return direction == "below"


def suggest_soil_upgrades(
    soil: dict,
    *,
    crop_data_csv: str | Path,
    market_csv: str | Path,
    exclude_crop: str | None = None,
    max_suggestions: int = 3,
    tolerance_frac: float = 1.0,
) -> list[dict]:
    """
    Return up to `max_suggestions` high-value crops the soil is almost suitable for.

    soil : {"N":, "P":, "K":, "ph":}

    A crop qualifies when exactly one controllable param (N/P/K/pH) is out of range,
    short by no more than `tolerance_frac` of that param's typical range width, and
    that gap is fixable (add fertilizer for a deficiency, or adjust pH either way).
    """
    try:
        profiles = load_crop_profiles(crop_data_csv)
        scores = market_value_score(market_csv)
    except Exception:
        return []

    excluded = _norm(exclude_crop) if exclude_crop else None
    suggestions: list[UpgradeSuggestion] = []

    for crop_key, profile in profiles.items():
        if crop_key == excluded:
            continue
        market = scores.get(crop_key)
        if market is None:
            continue  # no value signal -> skip

        # Evaluate controllable params: how many are out of range?
        out_params: list[tuple[str, str, float, float, float]] = []
        for param in CONTROLLABLE:
            rng = profile.ranges.get(param)
            val = soil.get(param)
            if rng is None or val is None:
                continue
            lo, hi = rng
            val = float(val)
            if val < lo:
                out_params.append((param, "below", val, lo, lo - val))
            elif val > hi:
                out_params.append((param, "above", val, hi, val - hi))

        # Need exactly one blocking param.
        if len(out_params) != 1:
            continue

        param, direction, current, target, gap = out_params[0]
        if not _is_fixable(param, direction):
            continue

        lo, hi = profile.ranges[param]
        width = max(hi - lo, 1e-6)
        if gap > tolerance_frac * width:
            continue  # too far off to be "almost" suitable

        suggestions.append(
            UpgradeSuggestion(
                crop=profile.crop,
                market_score=float(market["score"]),
                demand_level=market["demand_level"],
                price_per_kg=market["price_per_kg"],
                blocking_param=param,
                current_value=round(current, 2),
                target_value=round(target, 2),
                gap=round(gap, 2),
                action_text=amendment_for(param, direction, target),
            )
        )

    suggestions.sort(key=lambda s: s.market_score, reverse=True)
    return [asdict(s) for s in suggestions[:max_suggestions]]


def validate_soil(soil: dict) -> list[str]:
    """
    Return a list of human-readable problems with the soil inputs.
    Empty list means the inputs are within realistic agronomic ranges.
    """
    labels = {"N": "Nitrogen (N)", "P": "Phosphorus (P)", "K": "Potassium (K)", "ph": "pH"}
    warnings: list[str] = []
    for param, (lo, hi) in REALISTIC_BOUNDS.items():
        raw = soil.get(param)
        if raw is None:
            continue
        try:
            val = float(raw)
        except (TypeError, ValueError):
            warnings.append(f"{labels[param]} value '{raw}' is not a number.")
            continue
        if val < lo or val > hi:
            unit = "" if param == "ph" else " kg/ha"
            warnings.append(
                f"{labels[param]} = {val:g}{unit} is outside the realistic range "
                f"({lo:g}-{hi:g}{unit}). Please re-check the soil test value."
            )
    return warnings


def _crop_stats(data_csv: str | Path, params: tuple[str, ...]) -> dict[str, dict[str, tuple[float, float]]]:
    """Per-crop (mean, sigma) for the requested params, from the dataset."""
    df = pd.read_csv(data_csv)
    if "label" not in df.columns:
        return {}
    stats: dict[str, dict[str, tuple[float, float]]] = {}
    for label, group in df.groupby("label"):
        per_param: dict[str, tuple[float, float]] = {}
        for param in params:
            if param in group.columns:
                mean = float(group[param].mean())
                sigma = max(float(group[param].std(ddof=0)), _SIGMA_FLOOR[param])
                per_param[param] = (mean, sigma)
        stats[str(label)] = per_param
    return stats


def score_crops_by_soil(
    soil: dict,
    *,
    crop_data_csv: str | Path,
    climate: dict | None = None,
    climate_weight: float = 1.0,
    top_n: int = 3,
) -> list[dict]:
    """
    Rank crops by how well the soil chemistry (N/P/K/pH) - and, when provided,
    the season/region climate (temperature/humidity/rainfall) - match each crop's
    typical profile. Confidence is a 0-100 Gaussian-similarity score, so it
    responds to the inputs (unlike a hardcoded list) and stays low when the soil
    or climate is a poor match for every crop.

    `climate_weight` scales how strongly climate similarity counts relative to a
    single soil param (climate is the strongest regional discriminator, so the
    default weights each climate param the same as a soil param).
    """
    params = CONTROLLABLE + (CLIMATE_PARAMS if climate else tuple())
    try:
        stats = _crop_stats(crop_data_csv, params)
    except Exception:
        return []

    merged = {**soil, **(climate or {})}
    scored: list[tuple[str, float]] = []
    for crop, per_param in stats.items():
        if not per_param:
            continue
        total, weight_sum = 0.0, 0.0
        for param, (mean, sigma) in per_param.items():
            val = merged.get(param)
            if val is None:
                continue
            z = (float(val) - mean) / sigma
            s = float(np.exp(-0.5 * z * z))
            w = climate_weight if param in CLIMATE_PARAMS else 1.0
            total += s * w
            weight_sum += w
        if weight_sum == 0:
            continue
        scored.append((crop, total / weight_sum))

    scored.sort(key=lambda t: t[1], reverse=True)
    return [
        {"crop": crop, "confidence": int(round(score * 100))}
        for crop, score in scored[:top_n]
    ]
