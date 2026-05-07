from __future__ import annotations

from fastapi import APIRouter

from src.features.market_intelligence.api import router as market_router
from src.features.pest_warning.api import router as pest_router
from src.features.microclimate.api import router as micro_router

router = APIRouter()

router.include_router(market_router, prefix="/market", tags=["market"])
router.include_router(pest_router, prefix="/pest", tags=["pest"])
router.include_router(micro_router, prefix="/crop", tags=["microclimate"])

