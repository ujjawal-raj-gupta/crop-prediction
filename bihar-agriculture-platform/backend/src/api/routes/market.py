from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter

from src.api.schemas import MarketPredictRequest, MarketPredictResponse

router = APIRouter()


@router.post("/predict", response_model=MarketPredictResponse)
def predict(req: MarketPredictRequest):
    """
    MVP placeholder implementation.

    Next step: move your existing Streamlit market logic into `services/market_service.py`
    and call it from here.
    """
    today = date.today()
    base = 2150.0
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
    return {"crops": ["Wheat", "Rice", "Maize", "Mustard", "Lentils"]}


@router.get("/mandis")
def mandis():
    return {"mandis": ["Patna", "Muzaffarpur", "Bhagalpur", "Darbhanga", "Gaya"]}

