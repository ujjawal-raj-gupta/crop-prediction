from __future__ import annotations

from fastapi import APIRouter

from src.api.dashboard_api import router as dashboard_router
from src.api.support_api import router as support_router
from src.features.market_intelligence.api import router as market_router
from src.features.pest_warning.api import router as pest_router
from src.features.microclimate.api import router as micro_router

router = APIRouter()

router.include_router(market_router, prefix="/market", tags=["market"])
router.include_router(pest_router, prefix="/pest", tags=["pest"])
router.include_router(micro_router, prefix="/crop", tags=["microclimate"])
router.include_router(dashboard_router, prefix="/dashboard", tags=["dashboard"])
router.include_router(support_router, prefix="/support", tags=["support"])

