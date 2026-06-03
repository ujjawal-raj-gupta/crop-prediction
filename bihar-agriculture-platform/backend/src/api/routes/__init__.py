from __future__ import annotations

from fastapi import APIRouter

from src.api.routes.market import router as market_router
from src.api.routes.pest import router as pest_router
from src.api.routes.crop import router as crop_router
from src.api.routes.sensor import router as sensor_router
from src.api.routes.support import router as support_router

router = APIRouter()

router.include_router(market_router, prefix="/market", tags=["Market"])
router.include_router(pest_router, prefix="/pest", tags=["Pest"])
router.include_router(crop_router, prefix="/crop", tags=["Crop"])
router.include_router(sensor_router, prefix="/sensor", tags=["Sensor"])
router.include_router(support_router, prefix="/support", tags=["Support"])

