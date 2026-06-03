from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter

from src.api.schemas import CropRecommendRequest

router = APIRouter()

# Repo root holds the shared soil_advisor module + data/ CSVs.
# crop.py -> routes -> api -> src -> backend -> bihar-agriculture-platform -> repo root
REPO_ROOT = Path(__file__).resolve().parents[5]
DATA_DIR = REPO_ROOT / "data"
CROP_DATA_PATH = DATA_DIR / "crop_data.csv"
MARKET_PATH = DATA_DIR / "market_demand.csv"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# Season-typical climate for the Bihar plains, used to keep crop rankings
# regionally sensible (e.g. rice/jute in kharif, wheat/mustard in rabi) instead
# of surfacing climatically-implausible crops.
SEASON_CLIMATE = {
    "kharif": {"temperature": 30.0, "humidity": 80.0, "rainfall": 250.0},
    "rabi":   {"temperature": 20.0, "humidity": 60.0, "rainfall": 45.0},
    "zaid":   {"temperature": 35.0, "humidity": 50.0, "rainfall": 30.0},
}


def _data_source() -> Path:
    return CROP_DATA_PATH if CROP_DATA_PATH.exists() else (DATA_DIR / "Crop_recommendation.csv")


def _season_climate(req: CropRecommendRequest) -> dict | None:
    return SEASON_CLIMATE.get(str(getattr(req, "season", "") or "").strip().lower())


def _soil_from_request(req: CropRecommendRequest) -> dict:
    npk = req.soil_npk or {}
    return {
        "N": float(npk.get("n", npk.get("N", 0))),
        "P": float(npk.get("p", npk.get("P", 0))),
        "K": float(npk.get("k", npk.get("K", 0))),
        "ph": float(req.ph),
    }


def _irrigation_plan_for_crop(req: CropRecommendRequest, top_crop: str | None) -> dict | None:
    if not top_crop:
        return None
    try:
        from irrigation_plan import build_irrigation_plan_v2, plan_to_api_dict
        from src.services.weather_service import (
            fetch_daily_forecast,
            resolve_coords,
            synthetic_forecast_from_climate,
        )

        lat, lon = resolve_coords(req.district, req.latitude, req.longitude)
        forecast, weather_source = fetch_daily_forecast(lat, lon)
        if not forecast:
            climate = _season_climate(req) or {"temperature": 28.0, "humidity": 70.0, "rainfall": 100.0}
            forecast = synthetic_forecast_from_climate(
                float(climate["temperature"]),
                float(climate["humidity"]),
                float(climate["rainfall"]),
            )
            weather_source = "fallback"

        plan = build_irrigation_plan_v2(
            crop=str(top_crop),
            land_acres=float(getattr(req, "land_acres", 1.0) or 1.0),
            forecast_days=forecast,
        )
        return plan_to_api_dict(plan, weather_source=weather_source)
    except Exception:
        return None


def _upgrade_suggestions(req: CropRecommendRequest) -> list[dict]:
    """Compute soil upgrade suggestions, degrading gracefully if anything is missing."""
    try:
        from soil_advisor import suggest_soil_upgrades

        return suggest_soil_upgrades(
            _soil_from_request(req),
            crop_data_csv=_data_source(),
            market_csv=MARKET_PATH,
        )
    except Exception:
        return []


@router.post("/recommend")
def recommend(req: CropRecommendRequest):
    base = {
        "zone": "North Gangetic Plains",
        "zone_characteristics": {"flood_risk": "HIGH", "irrigation_pct": 65},
        "soil": {"npk": req.soil_npk, "ph": req.ph, "soil_type": req.soil_type},
    }

    try:
        from soil_advisor import load_market_info, score_crops_by_soil, validate_soil
    except Exception:
        # Shared module / data unavailable: cannot produce a real recommendation.
        return {
            **base,
            "recommendations": [],
            "warnings": ["Recommendation engine is unavailable on the server."],
            "input_valid": False,
            "upgrade_suggestions": [],
            "irrigation_plan": None,
        }

    soil = _soil_from_request(req)
    warnings = validate_soil(soil)

    # Reject physically implausible soil inputs instead of returning a confident
    # (but meaningless) recommendation.
    if warnings:
        return {
            **base,
            "recommendations": [],
            "warnings": warnings,
            "input_valid": False,
            "upgrade_suggestions": [],
            "irrigation_plan": None,
        }

    recommendations = score_crops_by_soil(
        soil,
        crop_data_csv=_data_source(),
        climate=_season_climate(req),
        top_n=8,
    )

    # Tell the farmer where to sell each recommended crop.
    try:
        market_info = load_market_info(MARKET_PATH)
    except Exception:
        market_info = {}
    for rec in recommendations:
        rec["market"] = market_info.get(str(rec.get("crop", "")).strip().lower())

    top_crop = recommendations[0]["crop"] if recommendations else None
    irrigation_plan = _irrigation_plan_for_crop(req, top_crop)

    return {
        **base,
        "season": getattr(req, "season", None),
        "recommendations": recommendations,
        "warnings": [],
        "input_valid": True,
        "upgrade_suggestions": _upgrade_suggestions(req),
        "irrigation_plan": irrigation_plan,
    }
