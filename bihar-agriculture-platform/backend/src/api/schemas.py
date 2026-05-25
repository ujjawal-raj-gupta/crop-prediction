from __future__ import annotations

from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class ApiEnvelope(BaseModel):
    status: Literal["success"] = "success"
    message: str | None = None


class ErrorEnvelope(BaseModel):
    status: Literal["error"] = "error"
    error: dict


class MarketPredictRequest(BaseModel):
    crop: str = Field(..., examples=["wheat"])
    mandi: str = Field(..., examples=["patna"])
    harvest_date: date | None = None
    quantity: float | None = None


class MarketPredictResponse(BaseModel):
    current_price: float
    predicted_prices: list[dict]
    recommendation: dict
    alternative_mandis: list[dict]


class PestRiskRequest(BaseModel):
    latitude: float
    longitude: float
    crop: str
    growth_stage: str


class CropRecommendRequest(BaseModel):
    """Soil + location for recommendation. Lat/lon default to Patna area if omitted (portal demo)."""

    latitude: float = Field(default=25.5941, ge=-90, le=90)
    longitude: float = Field(default=85.1376, ge=-180, le=180)
    soil_npk: dict
    soil_type: str
    ph: float
    season: str
    district: str | None = None

