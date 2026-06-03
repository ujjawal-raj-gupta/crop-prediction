"""Open-Meteo geocoding + daily forecast for irrigation scheduling."""

from __future__ import annotations

from datetime import date

import requests

from irrigation_plan import ForecastDay

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# Bihar district centroids (fallback when geocoding fails)
DISTRICT_COORDS: dict[str, tuple[float, float]] = {
    "patna": (25.5941, 85.1376),
    "muzaffarpur": (26.1209, 85.3647),
    "gaya": (24.7955, 85.0002),
    "bhagalpur": (25.2425, 86.9842),
    "darbhanga": (26.1542, 85.8918),
    "purnea": (25.7771, 87.4753),
    "purnia": (25.7771, 87.4753),
    "samastipur": (25.8620, 85.7810),
    "sitamarhi": (26.5950, 85.4808),
    "madhubani": (26.3480, 86.0710),
    "rohtas": (24.9600, 84.0210),
}


def geocode_district(district: str | None) -> tuple[float, float] | None:
    name = (district or "").strip()
    if not name:
        return None
    key = name.lower()
    if key in DISTRICT_COORDS:
        return DISTRICT_COORDS[key]

    try:
        resp = requests.get(
            GEOCODE_URL,
            params={"name": f"{name}, Bihar", "count": 1, "language": "en", "format": "json"},
            timeout=10,
        )
        resp.raise_for_status()
        results = resp.json().get("results") or []
        if results:
            return float(results[0]["latitude"]), float(results[0]["longitude"])
    except Exception:
        pass
    return None


def resolve_coords(
    district: str | None,
    latitude: float,
    longitude: float,
) -> tuple[float, float]:
    if district:
        coords = geocode_district(district)
        if coords:
            return coords
    return float(latitude), float(longitude)


def fetch_daily_forecast(lat: float, lon: float, days: int = 7) -> tuple[list[ForecastDay], str]:
    """
    Returns (forecast_days, weather_source).
    On failure returns synthetic dry-window days from empty list marker.
    """
    try:
        resp = requests.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": "temperature_2m_max,precipitation_sum,precipitation_probability_max",
                "forecast_days": days,
                "timezone": "Asia/Kolkata",
            },
            timeout=20,
        )
        resp.raise_for_status()
        data = resp.json()
        daily = data.get("daily") or {}
        times = daily.get("time") or []
        temps = daily.get("temperature_2m_max") or []
        precips = daily.get("precipitation_sum") or []
        probs = daily.get("precipitation_probability_max") or []

        out: list[ForecastDay] = []
        for i, t in enumerate(times):
            try:
                d = date.fromisoformat(str(t)[:10])
            except ValueError:
                continue
            temp = float(temps[i]) if i < len(temps) and temps[i] is not None else None
            precip = float(precips[i]) if i < len(precips) and precips[i] is not None else 0.0
            prob = float(probs[i]) if i < len(probs) and probs[i] is not None else None
            out.append(
                ForecastDay(
                    day=d,
                    temp_max_c=temp,
                    precip_mm=max(0.0, precip),
                    precip_prob_pct=prob,
                )
            )
        if out:
            return out, "open-meteo"
    except Exception:
        pass
    return [], "fallback"


def synthetic_forecast_from_climate(
    temperature_c: float,
    humidity_pct: float,
    rainfall_mm: float,
    days: int = 7,
) -> list[ForecastDay]:
    """Build placeholder daily rows when Open-Meteo is unavailable."""
    from datetime import timedelta

    today = date.today()
    # Higher seasonal rainfall -> more skip-like days in the synthetic window
    wet_bias = min(1.0, max(0.0, (rainfall_mm - 80.0) / 120.0))
    out: list[ForecastDay] = []
    for i in range(days):
        d = today + timedelta(days=i + 1)
        precip = 8.0 * wet_bias if i % 3 == 0 else 0.5
        prob = 70.0 * wet_bias if i % 3 == 0 else 20.0
        out.append(
            ForecastDay(
                day=d,
                temp_max_c=temperature_c,
                precip_mm=precip,
                precip_prob_pct=prob,
            )
        )
    return out
