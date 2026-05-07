from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select

from src.db.models import PriceHistory
from src.db.session import session_scope


router = APIRouter()


class MarketPredictRequest(BaseModel):
    crop: str = Field(..., examples=["wheat"])
    mandi: str = Field(..., examples=["muzaffarpur"])
    harvest_date: date | None = None
    quantity_quintals: float | None = None


class PredictedPrice(BaseModel):
    date: date
    price: float
    confidence_low: float
    confidence_high: float


class MarketPredictResponse(BaseModel):
    current_price: float | None
    predicted_prices: list[PredictedPrice]
    recommendation: dict
    alternative_mandis: list[dict] = []


@router.post("/predict", response_model=MarketPredictResponse)
def market_predict(req: MarketPredictRequest):
    crop = req.crop.strip().lower()
    mandi = req.mandi.strip().lower()

    # Baseline MVP: use last known modal price; forecast 30 days using flat + simple band.
    with session_scope() as s:
        row = s.execute(
            select(PriceHistory)
            .where(PriceHistory.crop == crop, PriceHistory.mandi == mandi)
            .order_by(desc(PriceHistory.date))
            .limit(1)
        ).scalar_one_or_none()

        if row is None or row.price_per_quintal is None:
            raise HTTPException(
                status_code=404,
                detail={
                    "error": "INSUFFICIENT_HISTORICAL_DATA",
                    "message": f"No stored price data for crop={crop}, mandi={mandi}. Ingest Agmarknet first.",
                },
            )

        current = float(row.price_per_quintal)

    horizon = 30
    today = date.today()
    preds: list[PredictedPrice] = []
    for i in range(1, horizon + 1):
        d = today + timedelta(days=i)
        # naive band +/-5%
        preds.append(
            PredictedPrice(
                date=d,
                price=current,
                confidence_low=round(current * 0.95, 2),
                confidence_high=round(current * 1.05, 2),
            )
        )

    rec = {
        "action": "HOLD",
        "optimal_sell_date": str(today + timedelta(days=14)),
        "expected_gain_percent": 0.0,
        "reasoning": "Baseline MVP forecast (flat) until advanced models are trained.",
    }

    return MarketPredictResponse(current_price=current, predicted_prices=preds, recommendation=rec)

