"""
Flask Web Dashboard (alternative to Streamlit)

Goal:
- Provide a dashboard-like UI (HTML/CSS) similar to the reference screenshot.
- Keep the same ML pipeline: load crop_model.pkl + soil_encoder.pkl and predict.
- Weather: city -> Open-Meteo geocoding -> Open-Meteo current weather (fallback if fails).
- Market insights: lookup predicted crop in data/market_demand.csv.

Run:
    python web_app.py
Then open:
    http://127.0.0.1:5000
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

import joblib
import pandas as pd
import requests
from flask import Flask, jsonify, render_template, request

from db import (
    enqueue_sms_jobs,
    fetch_due_pending_jobs_for_client,
    init_db,
    list_recent_jobs_for_client,
    mark_job_sent,
)
from irrigation_plan import build_irrigation_plan
from market_live import get_live_mandi_prices
from src.utils.config import load_dotenv_if_present


PROJECT_ROOT = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_ROOT / "crop_model.pkl"
ENCODER_PATH = PROJECT_ROOT / "soil_encoder.pkl"
FEATURE_COLS_PATH = PROJECT_ROOT / "feature_cols.pkl"
MARKET_PATH = PROJECT_ROOT / "data" / "market_demand.csv"

from features import build_model_input_row, default_feature_cols


app = Flask(__name__)
init_db()
# Load .env if present (local dev convenience for API keys).
load_dotenv_if_present()


@dataclass
class MarketInfo:
    demand_level: str = ""
    price_per_kg: str = ""
    buyer_type: str = ""
    buyer_location: str = ""


def demand_indicator(demand_level: str) -> tuple[str, str]:
    """
    Returns (badge_text, badge_class)
    badge_class is a Bootstrap-ish class name used in template CSS.
    """
    level = (demand_level or "").strip().lower()
    if level == "high":
        return "High", "badge-high"
    if level == "medium":
        return "Medium", "badge-medium"
    if level == "low":
        return "Low", "badge-low"
    return (demand_level or "N/A"), "badge-unknown"


def load_market_df() -> pd.DataFrame:
    if not MARKET_PATH.exists():
        return pd.DataFrame()
    df = pd.read_csv(MARKET_PATH)
    if "crop" in df.columns:
        df["crop_norm"] = df["crop"].astype(str).str.strip().str.lower()
    return df


def load_model_and_encoder():
    if not MODEL_PATH.exists() or not ENCODER_PATH.exists():
        raise FileNotFoundError(
            "Model files not found. Run Step 4 first:\n"
            "  python train_model.py\n"
            "Expected files:\n"
            f"  - {MODEL_PATH}\n"
            f"  - {ENCODER_PATH}\n"
        )
    model = joblib.load(MODEL_PATH)
    encoder = joblib.load(ENCODER_PATH)
    if FEATURE_COLS_PATH.exists():
        feature_cols = joblib.load(FEATURE_COLS_PATH)
    else:
        feature_cols = default_feature_cols()
    return model, encoder, feature_cols


def geocode_city(city: str) -> tuple[float, float] | None:
    city = city.strip()
    if not city:
        return None
    url = "https://geocoding-api.open-meteo.com/v1/search"
    params = {"name": city, "count": 1, "language": "en", "format": "json"}
    resp = requests.get(url, params=params, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results") or []
    if not results:
        return None
    return float(results[0]["latitude"]), float(results[0]["longitude"])


def get_weather(city: str) -> tuple[float, float, bool]:
    """
    Returns (temperature_c, humidity_percent, used_fallback)
    """
    try:
        coords = geocode_city(city)
        if coords is None:
            raise ValueError("City not found")
        lat, lon = coords
        url = "https://api.open-meteo.com/v1/forecast"
        params = {"latitude": lat, "longitude": lon, "current": "temperature_2m,relative_humidity_2m"}
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        current = data.get("current") or {}
        temp = float(current.get("temperature_2m"))
        hum = float(current.get("relative_humidity_2m"))
        return temp, hum, False
    except Exception:
        return 28.0, 75.0, True


def parse_float(form: dict, key: str, default: float) -> float:
    val = (form.get(key) or "").strip()
    if val == "":
        return default
    try:
        return float(val)
    except ValueError:
        return default


def parse_int(form: dict, key: str, default: int) -> int:
    val = (form.get(key) or "").strip()
    if val == "":
        return default
    try:
        return int(float(val))
    except ValueError:
        return default


@app.get("/")
def index_get():
    # Default city -> auto weather
    city = "Patna"
    temp, hum, used_fallback = get_weather(city)

    return render_template(
        "index.html",
        city=city,
        temperature=temp,
        humidity=hum,
        used_fallback=used_fallback,
        result=None,
        market=None,
        live_market=None,
        live_market_error=None,
        confidence=None,
        demand_badge=None,
        irrigation_plan=None,
        sms_enabled=False,
        sms_message=None,
        recent_sms=None,
        errors=[],
    )


@app.post("/predict")
def predict_post():
    errors: list[str] = []
    form = request.form

    city = (form.get("city") or "Patna").strip()
    soil_type = (form.get("soil_type") or "alluvial").strip().lower()
    client_id = (form.get("client_id") or "default").strip() or "default"
    sms_enabled = (form.get("sms_enabled") or "").strip() == "1"

    temperature = parse_float(form, "temperature", 28.0)
    humidity = parse_float(form, "humidity", 75.0)
    ph = parse_float(form, "ph", 6.5)
    rainfall = parse_float(form, "rainfall", 200.0)
    organic_matter = parse_float(form, "organic_matter", 2.0)

    n = parse_int(form, "n", 90)
    p = parse_int(form, "p", 42)
    k = parse_int(form, "k", 43)

    # Weather: optionally re-fetch if user pressed "fetch_weather" in the form
    used_fallback = False
    if form.get("fetch_weather") == "1":
        temperature, humidity, used_fallback = get_weather(city)

    try:
        model, encoder, feature_cols = load_model_and_encoder()
    except FileNotFoundError as e:
        errors.append(str(e))
        return render_template(
            "index.html",
            city=city,
            temperature=temperature,
            humidity=humidity,
            used_fallback=used_fallback,
            result=None,
            market=None,
            live_market=None,
            live_market_error=None,
            confidence=None,
            demand_badge=None,
            irrigation_plan=None,
            sms_enabled=sms_enabled,
            sms_message=None,
            recent_sms=list_recent_jobs_for_client(client_id=client_id) if client_id else None,
            errors=errors,
        )

    try:
        soil_encoded = int(encoder.transform([soil_type])[0])
    except Exception:
        errors.append(f"Invalid soil type: {soil_type}. Choose from alluvial/loamy/clay/sandy.")
        soil_encoded = 0

    X_input = build_model_input_row(
        n=n,
        p=p,
        k=k,
        temperature=float(temperature),
        humidity=float(humidity),
        ph=float(ph),
        rainfall=float(rainfall),
        soil_type_encoded=int(soil_encoded),
        organic_matter=float(organic_matter),
        feature_cols=list(feature_cols),
    )

    crop_pred = model.predict(X_input)[0]

    confidence = None
    if hasattr(model, "predict_proba"):
        proba = model.predict_proba(X_input)[0]
        confidence = float(proba.max())

    live_market, live_market_error = get_live_mandi_prices(crop_label=str(crop_pred), state="Bihar")

    # Build irrigation plan
    plan = build_irrigation_plan(
        crop=str(crop_pred),
        temperature_c=float(temperature),
        humidity_pct=float(humidity),
        rainfall_mm=float(rainfall),
        tz="Asia/Kolkata",
        horizon_events=3,
    )
    irrigation_plan = [
        {"when_local": ev.when.strftime("%Y-%m-%d %I:%M %p"), "note": ev.note, "when_iso": ev.when.isoformat()}
        for ev in plan.events
    ]

    sms_message = None
    if sms_enabled:
        # Fake SMS popup: capture click time on server, schedule a single popup at click+2 minutes.
        created_at_utc = datetime.now(timezone.utc).replace(tzinfo=None)
        when_utc_dt = created_at_utc + timedelta(minutes=2)
        when_utc = when_utc_dt.isoformat(sep=" ")
        body = f"SMS: Crop predicted '{crop_pred}'. Reminder created at {created_at_utc.isoformat(sep=' ')} UTC."
        jobs = [{"when_utc": when_utc, "body": body}]
        inserted = enqueue_sms_jobs(
            to_number="fake",
            crop=str(crop_pred),
            jobs=jobs,
            client_id=client_id,
        )
        sms_message = f"Scheduled {inserted} in-app SMS popup reminder(s) for click time + 2 minutes."

    market = None
    demand_badge = None
    market_df = load_market_df()
    if not market_df.empty and "crop_norm" in market_df.columns:
        row = market_df[market_df["crop_norm"] == str(crop_pred).strip().lower()]
        if not row.empty:
            r = row.iloc[0].to_dict()
            market = MarketInfo(
                demand_level=str(r.get("demand_level", "")),
                price_per_kg=str(r.get("price_per_kg", "")),
                buyer_type=str(r.get("buyer_type", "")),
                buyer_location=str(r.get("buyer_location", "")),
            )
            demand_badge = demand_indicator(market.demand_level)

    return render_template(
        "index.html",
        city=city,
        temperature=temperature,
        humidity=humidity,
        used_fallback=used_fallback,
        result=str(crop_pred),
        market=market,
        live_market=live_market,
        live_market_error=live_market_error,
        confidence=confidence,
        demand_badge=demand_badge,
        irrigation_plan=irrigation_plan,
        sms_enabled=sms_enabled,
        sms_message=sms_message,
        recent_sms=list_recent_jobs_for_client(client_id=client_id) if client_id else None,
        errors=errors,
        # keep form values
        n=n,
        p=p,
        k=k,
        ph=ph,
        rainfall=rainfall,
        soil_type=soil_type,
        organic_matter=organic_matter,
        client_id=client_id,
    )


@app.get("/api/notifications")
def notifications_get():
    """
    Returns due "fake SMS" notifications for this browser client_id.
    """
    client_id = (request.args.get("client_id") or "default").strip() or "default"
    rows = fetch_due_pending_jobs_for_client(client_id=client_id, limit=10)
    payload = []
    for r in rows:
        payload.append({"id": int(r["id"]), "body": str(r["body"]), "when_utc": str(r["when_utc"])})
    return jsonify({"notifications": payload})


@app.post("/api/notifications/ack")
def notifications_ack():
    """
    Mark a notification as "sent" after it has been shown in the UI.
    """
    data = request.get_json(silent=True) or {}
    try:
        job_id = int(data.get("id"))
    except Exception:
        return jsonify({"ok": False, "error": "Invalid id"}), 400
    mark_job_sent(job_id=job_id)
    return jsonify({"ok": True})


if __name__ == "__main__":
    # debug=True for development (auto-reload + better errors)
    # Bind to all interfaces so it can be opened via LAN IP too.
    # Use PORT env var for cloud providers (Render/Heroku/etc.)
    import os

    port = int(os.getenv("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)

