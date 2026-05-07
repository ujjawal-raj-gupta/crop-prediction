from __future__ import annotations

from fastapi import APIRouter
from pydantic import BaseModel


router = APIRouter()


class AdaptiveCropRequest(BaseModel):
    latitude: float
    longitude: float
    soil_npk: dict
    soil_type: str
    ph: float
    season: str


@router.post("/recommend-adaptive")
def recommend_adaptive(req: AdaptiveCropRequest):
    # MVP placeholder:
    # - Zone detection will be implemented once we ingest Bihar district/zone datasets.
    # - For now, return a safe stub response so the API is runnable.
    zone_id = "zone_0_default"
    return {
        "detected_zone": zone_id,
        "zone_characteristics": {
            "note": "MVP stub until clustering datasets are added (IMD/NASA POWER + soil/terrain)."
        },
        "recommendations": [],
        "model_used": "generic_model_v0",
    }

