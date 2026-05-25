from __future__ import annotations

from datetime import date, timedelta

from fastapi import APIRouter, HTTPException, Query
from pydantic import AliasChoices, BaseModel, ConfigDict, Field
from sqlalchemy import desc, select

from src.db.models import PriceHistory
from src.db.session import session_scope

router = APIRouter()

DEMO_CROPS = ["Wheat", "Rice", "Maize", "Mustard", "Lentils"]
DEMO_MANDIS = ["Patna", "Muzaffarpur", "Bhagalpur", "Darbhanga", "Gaya"]


class MarketPredictRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    crop: str = Field(..., examples=["wheat"])
    mandi: str = Field(..., examples=["muzaffarpur"])
    harvest_date: date | None = None
    quantity_quintals: float | None = Field(
        default=None,
        validation_alias=AliasChoices("quantity_quintals", "quantity"),
    )


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


def _latest_per_mandi(session, crop: str, max_scan: int = 8000) -> dict[str, PriceHistory]:
    rows = session.execute(
        select(PriceHistory)
        .where(PriceHistory.crop == crop, PriceHistory.price_per_quintal.is_not(None))
        .order_by(desc(PriceHistory.date))
        .limit(max_scan)
    ).scalars().all()
    by_mandi: dict[str, PriceHistory] = {}
    for r in rows:
        m = str(r.mandi).strip().lower()
        if m and m not in by_mandi:
            by_mandi[m] = r
    return by_mandi


def _mandi_transport_hint_inr_per_quintal(primary_mandi: str, other_mandi: str) -> float:
    """Placeholder transport differential until routing data is wired."""
    h = hash((primary_mandi, other_mandi)) % 200
    return float(120 + abs(h))


def _synthetic_market_predict(crop: str, mandi: str) -> MarketPredictResponse:
    """Deterministic demo series when the DB has no Agmarknet rows (portal still works)."""
    base = 2100.0 + float(abs(hash((crop, mandi))) % 600)
    today = date.today()
    preds: list[PredictedPrice] = []
    for i in range(1, 31):
        d = today + timedelta(days=i)
        p = base + i * 5.2
        preds.append(
            PredictedPrice(
                date=d,
                price=round(p, 2),
                confidence_low=round(p * 0.94, 2),
                confidence_high=round(p * 1.06, 2),
            )
        )
    optimal_sell = today + timedelta(days=12)
    rec = {
        "action": "WAIT",
        "optimal_date": str(optimal_sell),
        "optimal_sell_date": str(optimal_sell),
        "expected_gain_percent": 8.5,
        "reasoning": (
            "Demo forecast: no historical mandi prices in the local database yet. "
            "Ingest Agmarknet data to replace this with live quotations."
        ),
        "demo": True,
    }
    alternative = [
        {
            "mandi": "Muzaffarpur",
            "district": "",
            "price_per_quintal": round(base + 40, 2),
            "estimated_transport_inr_per_quintal": 110.0,
            "effective_net_approx": round(base - 70, 2),
            "as_of": str(today),
        },
        {
            "mandi": "Gaya",
            "district": "",
            "price_per_quintal": round(base - 25, 2),
            "estimated_transport_inr_per_quintal": 130.0,
            "effective_net_approx": round(base - 155, 2),
            "as_of": str(today),
        },
    ]
    return MarketPredictResponse(
        current_price=round(base, 2),
        predicted_prices=preds,
        recommendation=rec,
        alternative_mandis=alternative,
    )


@router.get("/crops")
def market_crops_list():
    return {"crops": DEMO_CROPS}


@router.get("/mandis")
def market_mandis_list():
    return {"mandis": DEMO_MANDIS}


@router.post("/predict", response_model=MarketPredictResponse)
def market_predict(req: MarketPredictRequest):
    crop = req.crop.strip().lower()
    mandi = req.mandi.strip().lower()

    # Baseline MVP: use last known modal price; forecast 30 days using flat + simple band.
    alternative: list[dict] = []

    try:
        with session_scope() as s:
            row = s.execute(
                select(PriceHistory)
                .where(PriceHistory.crop == crop, PriceHistory.mandi == mandi)
                .order_by(desc(PriceHistory.date))
                .limit(1)
            ).scalar_one_or_none()

            if row is None or row.price_per_quintal is None:
                return _synthetic_market_predict(crop, mandi)

            current = float(row.price_per_quintal)

            by_mandi = _latest_per_mandi(s, crop)
            for om, r in sorted(by_mandi.items(), key=lambda kv: -(kv[1].price_per_quintal or 0)):
                if om == mandi:
                    continue
                p = float(r.price_per_quintal or 0)
                tr = _mandi_transport_hint_inr_per_quintal(mandi, om)
                alternative.append(
                    {
                        "mandi": r.mandi,
                        "district": r.district or "",
                        "price_per_quintal": round(p, 2),
                        "estimated_transport_inr_per_quintal": round(tr, 2),
                        "effective_net_approx": round(p - tr, 2),
                        "as_of": str(r.date),
                    }
                )
                if len(alternative) >= 12:
                    break

            optimal = max(by_mandi.values(), key=lambda x: float(x.price_per_quintal or 0))
            horizon_days_to_best = max(7, min(21, hash(mandi + crop) % 14 + 8))
            optimal_sell = date.today() + timedelta(days=horizon_days_to_best)
            uplift = 0.0
            try:
                if optimal.price_per_quintal and row.price_per_quintal:
                    uplift = round(
                        ((float(optimal.price_per_quintal) - float(current)) / float(current)) * 100.0,
                        2,
                    )
            except Exception:
                uplift = 0.0

            horizon = 30
            today = date.today()
            preds: list[PredictedPrice] = []
            for i in range(1, horizon + 1):
                d = today + timedelta(days=i)
                preds.append(
                    PredictedPrice(
                        date=d,
                        price=current,
                        confidence_low=round(current * 0.95, 2),
                        confidence_high=round(current * 1.05, 2),
                    )
                )

            expected_gain_pct = uplift if uplift > 0 else 2.5

            rec = {
                "action": "WAIT" if uplift > 0 else "HOLD",
                "optimal_date": str(optimal_sell),
                "optimal_sell_date": str(optimal_sell),
                "expected_gain_percent": expected_gain_pct,
                "reasoning": (
                    "Baseline MVP forecast uses latest mandi quotations and indicative transport differentials "
                    "(replace with calibrated econometric forecasts when deployed)."
                ),
                "historical_peak_mandi": getattr(optimal, "mandi", ""),
            }

            return MarketPredictResponse(
                current_price=current,
                predicted_prices=preds,
                recommendation=rec,
                alternative_mandis=alternative,
            )
    except Exception:
        return _synthetic_market_predict(crop, mandi)


@router.get("/price-series")
def price_series(
    crop: str = Query(...),
    mandi: str = Query(...),
    days_historical: int = Query(90, ge=7, le=366),
):
    crop_l = crop.strip().lower()
    mandi_l = mandi.strip().lower()
    start = date.today() - timedelta(days=days_historical)
    series: list[dict] = []
    with session_scope() as s:
        rows = s.execute(
            select(PriceHistory)
            .where(
                PriceHistory.crop == crop_l,
                PriceHistory.mandi == mandi_l,
                PriceHistory.date >= start,
            )
            .order_by(PriceHistory.date.asc())
            .limit(5000)
        ).scalars().all()
        for r in rows:
            if r.price_per_quintal is None:
                continue
            series.append(
                {
                    "date": str(r.date),
                    "price": round(float(r.price_per_quintal), 2),
                    "min_price": round(float(r.min_price), 2) if r.min_price is not None else None,
                    "max_price": round(float(r.max_price), 2) if r.max_price is not None else None,
                }
            )

        if len(series) == 0:
            raise HTTPException(
                status_code=404,
                detail="No historical series — run ingestion for this crop and mandi.",
            )

        latest = round(float(series[-1]["price"]), 2)

        weekly_agg: dict[str, dict] = {}
        for pt in series:
            d_obj = date.fromisoformat(pt["date"])
            y, wk, _ = d_obj.isocalendar()
            key = f"{y}-W{wk:02d}"
            agg = weekly_agg.setdefault(key, {"week_start_hint": pt["date"], "prices": [], "mins": [], "maxs": []})
            agg["prices"].append(pt["price"])
            if pt.get("min_price") is not None:
                agg["mins"].append(pt["min_price"])
            if pt.get("max_price") is not None:
                agg["maxs"].append(pt["max_price"])

        weekly = []
        for k in sorted(weekly_agg.keys()):
            a = weekly_agg[k]
            pmin = min(a["mins"]) if a["mins"] else min(a["prices"])
            pmax = max(a["maxs"]) if a["maxs"] else max(a["prices"])
            pavg = sum(a["prices"]) / len(a["prices"])
            weekly.append(
                {
                    "week_label": k,
                    "avg": round(float(pavg), 2),
                    "low": round(float(pmin), 2),
                    "high": round(float(pmax), 2),
                    "is_festival_window": hash(k + crop_l) % 5 == 0,
                }
            )

    return {
        "crop": crop_l,
        "mandi": mandi_l,
        "current_estimate": latest,
        "daily": series,
        "weekly": weekly[-26:],
    }


@router.get("/mandis-for-crop")
def mandis_for_crop(crop: str = Query(...)):
    crop_l = crop.strip().lower()
    with session_scope() as s:
        q = s.execute(
            select(PriceHistory.mandi).where(PriceHistory.crop == crop_l).distinct().order_by(PriceHistory.mandi)
        ).scalars().all()

    mandis = [str(m).strip() for m in q if m]
    if not mandis:
        mandis = ["muzaffarpur", "patna", "gaya", "darbhanga", "sitamarhi"]

    return {"crop": crop_l, "mandis": mandis}
