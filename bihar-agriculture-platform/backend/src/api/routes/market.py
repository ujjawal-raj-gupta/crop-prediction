from __future__ import annotations

import csv
import sys
from datetime import date, timedelta
from pathlib import Path

from fastapi import APIRouter

from src.api.schemas import MarketPredictRequest, MarketPredictResponse

router = APIRouter()

# Repo root holds the shared data/ CSVs.
# market.py -> routes -> api -> src -> backend -> bihar-agriculture-platform -> repo root
REPO_ROOT = Path(__file__).resolve().parents[5]
DATA_DIR = REPO_ROOT / "data"
MARKET_PATH = DATA_DIR / "market_demand.csv"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


MANDI_PATH = DATA_DIR / "mandi_prices.csv"


def _load_mandi_prices() -> list[dict]:
    """
    Load the mandi-level price data: actual Bihar mandis, districts, buyer types,
    price per quintal and sell tips.
    """
    if not MANDI_PATH.exists():
        return []
    rows: list[dict] = []
    with MANDI_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            crop = (row.get("crop") or "").strip()
            if not crop:
                continue
            try:
                price = float(row.get("price_per_quintal") or 0)
            except (TypeError, ValueError):
                price = 0.0
            rows.append(
                {
                    "crop": crop,
                    "mandi": (row.get("mandi") or "").strip(),
                    "district": (row.get("district") or "").strip(),
                    "buyer_type": (row.get("buyer_type") or "").strip(),
                    "price_per_quintal": price,
                    "notes": (row.get("notes") or "").strip(),
                }
            )
    return rows


def _load_buyers() -> list[dict]:
    """Read the buyer/where-to-sell directory from data/market_demand.csv."""
    if not MARKET_PATH.exists():
        return []
    rows: list[dict] = []
    with MARKET_PATH.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            crop = (row.get("crop") or "").strip()
            if not crop:
                continue
            try:
                price = float(row.get("price_per_kg") or 0)
            except (TypeError, ValueError):
                price = 0.0
            rows.append(
                {
                    "crop": crop,
                    "demand_level": (row.get("demand_level") or "").strip(),
                    "price_per_kg": price,
                    "buyer_type": (row.get("buyer_type") or "").strip(),
                    "buyer_location": (row.get("buyer_location") or "").strip(),
                }
            )
    return rows


@router.post("/predict", response_model=MarketPredictResponse)
def predict(req: MarketPredictRequest):
    """
    MVP placeholder implementation.

    Next step: move your existing Streamlit market logic into `services/market_service.py`
    and call it from here.
    """
    today = date.today()

    # Anchor the forecast to the crop's real price (Rs/kg -> Rs/quintal) when known,
    # so the "current price" reflects actual market data instead of a fixed demo value.
    base = 2150.0
    for b in _load_buyers():
        if b["crop"].strip().lower() == str(getattr(req, "crop", "") or "").strip().lower():
            if b["price_per_kg"] > 0:
                base = round(b["price_per_kg"] * 100.0, 2)
            break

    forecast = []
    for i in range(1, 31):
        d = today + timedelta(days=i)
        p = base + i * 6.5
        forecast.append(
            {
                "date": str(d),
                "price": round(p, 2),
                "confidence_low": round(p * 0.94, 2),
                "confidence_high": round(p * 1.06, 2),
            }
        )

    rec = {
        "action": "WAIT",
        "optimal_date": str(today + timedelta(days=12)),
        "expected_gain_percent": 12.6,
        "reasoning": "Demo logic until production forecasting model is wired.",
    }

    mandis = [
        {"mandi": "patna", "price_per_quintal": 2210, "transport_cost_inr": 90},
        {"mandi": "muzaffarpur", "price_per_quintal": 2195, "transport_cost_inr": 110},
        {"mandi": "gaya", "price_per_quintal": 2140, "transport_cost_inr": 130},
    ]

    return MarketPredictResponse(
        current_price=base,
        predicted_prices=forecast,
        recommendation=rec,
        alternative_mandis=mandis,
    )


@router.get("/crops")
def crops():
    buyers = _load_buyers()
    if buyers:
        names = sorted({b["crop"].title() for b in buyers})
        return {"crops": names}
    return {"crops": ["Wheat", "Rice", "Maize", "Mustard", "Lentils"]}


@router.get("/buyers")
def buyers():
    """
    Where-to-sell directory: for every crop, who buys it, where, the going
    price (Rs/kg) and current demand. Sourced from data/market_demand.csv.
    """
    return {"buyers": _load_buyers()}


@router.get("/mandi-prices")
def mandi_prices(crop: str | None = None, district: str | None = None):
    """
    Mandi-level price board for Bihar.
    Returns specific mandi names, districts, buyer types, price/quintal and tips.
    Optional filters: ?crop=rice  ?district=Patna
    """
    rows = _load_mandi_prices()
    if crop:
        rows = [r for r in rows if r["crop"].lower() == crop.strip().lower()]
    if district:
        rows = [r for r in rows if district.strip().lower() in r["district"].lower()]
    # Unique districts for filter dropdown
    districts = sorted({r["district"] for r in _load_mandi_prices()})
    crops = sorted({r["crop"] for r in _load_mandi_prices()})
    return {"mandi_prices": rows, "districts": districts, "crops": crops}


@router.get("/mandis")
def mandis():
    return {"mandis": ["Patna", "Muzaffarpur", "Bhagalpur", "Darbhanga", "Gaya"]}

