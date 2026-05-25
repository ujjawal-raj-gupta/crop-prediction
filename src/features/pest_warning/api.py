from __future__ import annotations

import json
from pathlib import Path

import requests
from fastapi import APIRouter
from pydantic import BaseModel, Field

from src.db.models import PestAlert
from src.db.session import session_scope
from src.features.pest_warning.suggestions import (
    build_threat,
    recommendation_set_for,
    risk_level,
    tier_advice,
)

router = APIRouter()

KB_PATH = Path(__file__).resolve().parent / "pest_knowledge_base.json"


class PestRiskRequest(BaseModel):
    latitude: float
    longitude: float
    crop: str
    growth_stage: str = Field(..., examples=["tillering"])
    farm_id: str | None = None


class WeatherWindowRequest(BaseModel):
    latitude: float
    longitude: float


def _open_meteo_forecast(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "hourly": "temperature_2m,relative_humidity_2m,precipitation_probability,precipitation",
        "forecast_days": 3,
        "timezone": "Asia/Kolkata",
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def _open_meteo_7day_daily(lat: float, lon: float) -> dict:
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": ",".join(
            [
                "temperature_2m_max",
                "temperature_2m_min",
                "precipitation_probability_max",
                "precipitation_sum",
                "weathercode",
            ]
        ),
        "forecast_days": 7,
        "timezone": "Asia/Kolkata",
    }
    r = requests.get(url, params=params, timeout=20)
    r.raise_for_status()
    return r.json()


def _load_kb() -> dict:
    return json.loads(KB_PATH.read_text(encoding="utf-8"))


DISTRICT_WEIGHTS_BIHAR: list[tuple[str, float]] = [
    ("Patna", 0.92),
    ("Muzaffarpur", 0.88),
    ("Gaya", 0.71),
    ("Bhagalpur", 0.66),
    ("Darbhanga", 0.79),
    ("Purnea", 0.73),
    ("Sitamarhi", 0.65),
    ("Samastipur", 0.7),
    ("Madhubani", 0.68),
    ("Rohtas", 0.55),
]


@router.post("/check-risk")
def check_risk(req: PestRiskRequest):
    crop = req.crop.strip().lower()
    stage = req.growth_stage.strip().lower()

    kb = _load_kb()
    weather = _open_meteo_forecast(req.latitude, req.longitude)
    hourly = weather.get("hourly") or {}
    temps = hourly.get("temperature_2m") or []
    hums = hourly.get("relative_humidity_2m") or []
    temp_avg = sum(temps) / len(temps) if temps else None
    hum_avg = sum(hums) / len(hums) if hums else None

    threats = []
    overall = 0

    for pest_key, meta in kb.items():
        if crop not in [c.lower() for c in (meta.get("affected_crops") or [])]:
            continue
        triggers = meta.get("weather_triggers") or {}
        humidity_min = float(triggers.get("humidity_min", 0))
        tmin = float(triggers.get("temp_min", -999))
        tmax = float(triggers.get("temp_max", 999))

        stage_match = stage in [s.lower() for s in (meta.get("vulnerable_stages") or [])]
        humidity_match = hum_avg is not None and hum_avg >= humidity_min
        temp_match = temp_avg is not None and (tmin <= temp_avg <= tmax)

        score = 0
        if stage_match:
            score += 25
        if humidity_match:
            score += 35
        if temp_match:
            score += 35
        score = min(score, 100)

        if score > 0:
            threat = build_threat(
                pest_key,
                meta,
                score=score,
                factors={
                    "weather_humidity_avg": hum_avg,
                    "weather_temp_avg": temp_avg,
                    "growth_stage_vulnerable": stage_match,
                    "humidity_trigger_met": humidity_match,
                    "temp_trigger_met": temp_match,
                },
            )
            threats.append(threat)
            overall = max(overall, score)

    # Sort threats by risk so high-priority ones surface first
    threats.sort(key=lambda t: t["risk_score"], reverse=True)
    overall_level = risk_level(overall)

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

    wf7 = {}
    try:
        wf7_raw = _open_meteo_7day_daily(req.latitude, req.longitude)
        wf7 = {
            "dates": wf7_raw.get("daily", {}).get("time") or [],
            "temp_max": wf7_raw.get("daily", {}).get("temperature_2m_max") or [],
            "temp_min": wf7_raw.get("daily", {}).get("temperature_2m_min") or [],
            "rain_prob_pct": wf7_raw.get("daily", {}).get("precipitation_probability_max") or [],
            "rain_mm": wf7_raw.get("daily", {}).get("precipitation_sum") or [],
        }
    except Exception:
        wf7 = {"dates": [], "temp_max": [], "temp_min": [], "rain_prob_pct": [], "rain_mm": []}

    return {
        "overall_risk": overall,
        "risk_level": overall_level,
        "threats": threats,
        "recommendation_set": recommendation_set_for(overall_level),
        "tier_advice": tier_advice(overall_level),
        "weather_forecast": {
            "temp_avg_next_3_days": temp_avg,
            "humidity_avg_next_3_days": hum_avg,
        },
        "weather_7_day": wf7,
        "input_echo": {
            "crop": crop,
            "growth_stage": stage,
            "latitude": req.latitude,
            "longitude": req.longitude,
        },
    }


@router.post("/weather-7-day")
def weather_7_day(req: WeatherWindowRequest):
    wf7_raw = _open_meteo_7day_daily(req.latitude, req.longitude)
    d = wf7_raw.get("daily") or {}
    days = []
    for i in range(len(d.get("time") or [])):
        tmax = d.get("temperature_2m_max") or []
        tmin = d.get("temperature_2m_min") or []
        probs = d.get("precipitation_probability_max") or []
        rain = d.get("precipitation_sum") or []
        t_hi = float(tmax[i]) if i < len(tmax) else None
        t_lo = float(tmin[i]) if i < len(tmin) else None
        prob = float(probs[i]) if i < len(probs) else 0
        rn = float(rain[i]) if i < len(rain) else 0
        t_mid = (t_hi + t_lo) / 2 if t_hi is not None and t_lo is not None else t_hi or t_lo
        humid_proxy = max(35.0, min(95.0, 92.0 - (t_mid or 25) + prob * 0.15))
        days.append(
            {
                "date": d["time"][i],
                "temp_avg_c": round(float(t_mid or 28), 1),
                "humidity_pct": round(float(humid_proxy), 1),
                "rain_probability_pct": round(float(prob), 1),
                "rain_mm": round(float(rn), 1),
                "pest_favorable": bool(t_mid is not None and humid_proxy >= 75 and (t_mid >= 26 or prob >= 50)),
            }
        )

    return {"days": days}


@router.post("/regional-outline")
def regional_outline(req: PestRiskRequest):
    """Synthetic district scores for choropleth (replace with sentinel / district models)."""
    base = req.crop.strip().lower()
    out = []
    for dist, bw in DISTRICT_WEIGHTS_BIHAR:
        jitter = abs(hash(dist + base) % 35) / 100.0
        score = round(min(99.9, bw * 100 * (0.7 + jitter / 5)), 1)
        out.append({"district": dist, "risk_score": score, "level": ("high" if score >= 65 else "medium" if score >= 35 else "low")})
    out.sort(key=lambda x: x["risk_score"], reverse=True)
    return {"districts": out, "center_hint": {"lat": req.latitude, "lon": req.longitude}}
