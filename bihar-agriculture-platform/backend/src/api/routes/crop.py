from __future__ import annotations

from fastapi import APIRouter

from src.api.schemas import CropRecommendRequest

router = APIRouter()


@router.post("/recommend")
def recommend(req: CropRecommendRequest):
    # MVP placeholder: replace with trained model + zone datasets
    return {
        "zone": "North Gangetic Plains",
        "zone_characteristics": {"flood_risk": "HIGH", "irrigation_pct": 65},
        "recommendations": [
            {"crop": "Wheat", "confidence": 89, "expected_yield_quintals_acre": 42},
            {"crop": "Mustard", "confidence": 76, "expected_yield_quintals_acre": 18},
            {"crop": "Lentils", "confidence": 71, "expected_yield_quintals_acre": 12},
        ],
        "soil": {"npk": req.soil_npk, "ph": req.ph, "soil_type": req.soil_type},
    }

