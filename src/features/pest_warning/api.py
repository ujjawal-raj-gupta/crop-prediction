from __future__ import annotations

import json
from pathlib import Path

import requests
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.db.models import PestAlert
from src.db.session import session_scope


router = APIRouter()

KB_PATH = Path(__file__).resolve().parent / "pest_knowledge_base.json"


class PestRiskRequest(BaseModel):
    latitude: float
    longitude: float
    crop: str
    growth_stage: str = Field(..., examples=["tillering"])
    farm_id: str | None = None


def _open_meteo_forecast(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation",
        "forecast_days": 3,
        "timezone": "auto",
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def _load_kb() -> dict:
    return json.loads(KB_PATH.read_text(encoding="utf-8"))


@router.post("/check-risk")
def check_risk(req: PestRiskRequest):
    crop = req.crop.strip().lower()
    stage = req.growth_stage.strip().lower()

    kb = _load_kb()
    weather = _open_meteo_forecast(req.latitude, req.longitude)
    hourly = (weather.get("hourly") or {})
    temps = hourly.get("temperature_2m") or []
    hums = hourly.get("relative_humidity_2m") or []
    temp_avg = sum(temps) / len(temps) if temps else None
    hum_avg = sum(hums) / len(hums) if hums else None

    threats = []
    overall = 0

    for pest_name, meta in kb.items():
        if crop not in [c.lower() for c in (meta.get("affected_crops") or [])]:
            continue
        triggers = meta.get("weather_triggers") or {}
        humidity_min = float(triggers.get("humidity_min", 0))
        tmin = float(triggers.get("temp_min", -999))
        tmax = float(triggers.get("temp_max", 999))

        score = 0
        if stage in [s.lower() for s in (meta.get("vulnerable_stages") or [])]:
            score += 25
        if hum_avg is not None and hum_avg >= humidity_min:
            score += 35
        if temp_avg is not None and (tmin <= temp_avg <= tmax):
            score += 35
        if score > 100:
            score = 100

        if score > 0:
            threats.append(
                {
                    "pest_name": pest_name.replace("_", " ").title(),
                    "risk_score": score,
                    "factors": {
                        "weather_humidity_avg": hum_avg,
                        "weather_temp_avg": temp_avg,
                        "growth_stage_vulnerable": stage
                        in [s.lower() for s in (meta.get("vulnerable_stages") or [])],
                    },
                    "symptoms": meta.get("symptoms"),
                    "treatment": meta.get("treatment"),
                }
            )
            overall = max(overall, score)

    risk_level = "LOW" if overall <= 30 else ("MEDIUM" if overall <= 60 else "HIGH")

    # Persist a record for tracking (optional but useful)
    with session_scope() as s:
        if overall > 0:
            s.add(
                PestAlert(
                    latitude=req.latitude,
                    longitude=req.longitude,
                    crop=crop,
                    pest_name=threats[0]["pest_name"] if threats else "unknown",
                    risk_score=int(overall),
                    farmer_id=req.farm_id,
                    details={"threats": threats},
                )
            )

    return {
        "overall_risk": overall,
        "risk_level": risk_level,
        "threats": threats,
        "weather_forecast": {
            "temp_avg_next_3_days": temp_avg,
            "humidity_avg_next_3_days": hum_avg,
        },
    }

