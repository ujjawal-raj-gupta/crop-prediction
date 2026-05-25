"""Pest risk endpoint (MVP backend).

Loads the canonical knowledge base from the repo-root location (a single
source of truth for both backends) and returns the same suggestion-rich
response shape consumed by the React frontend and the static portal.

This module does **not** import from the root backend's ``src`` package
because both stacks define a top-level ``src`` namespace which would
collide at import time. Instead the suggestion helpers live in
:mod:`src.utils.pest_kb` here in the MVP backend (a small, pure copy).
"""

from __future__ import annotations

from fastapi import APIRouter

from src.api.schemas import PestRiskRequest
from src.utils.pest_kb import (
    build_threat,
    load_kb,
    recommendation_set_for,
    risk_level,
    tier_advice,
)


router = APIRouter()


@router.post("/check-risk")
def check_risk(req: PestRiskRequest):
    """Score pests for the (crop, stage) pair using the shared knowledge base.

    The MVP backend has no live weather feed, so it scores purely on
    crop + growth-stage match. The root FastAPI backend layers Open-Meteo
    on top of the same KB for fuller scoring. The response shape is
    identical between both backends so UI code can stay backend-agnostic.
    """

    crop = (req.crop or "").strip().lower()
    stage = (req.growth_stage or "").strip().lower()
    kb = load_kb()

    threats: list[dict] = []
    overall = 0

    for pest_key, meta in kb.items():
        if crop not in [c.lower() for c in (meta.get("affected_crops") or [])]:
            continue

        # MVP scoring without weather: base 40 for any matching crop, +35
        # if the user's growth stage also matches a vulnerable phase.
        score = 40
        stage_match = stage in [s.lower() for s in (meta.get("vulnerable_stages") or [])]
        if stage_match:
            score += 35
        score = min(score, 100)

        threats.append(
            build_threat(
                pest_key,
                meta,
                score=score,
                factors={
                    "growth_stage_vulnerable": stage_match,
                    "source": "mvp_backend_no_weather",
                },
            )
        )
        overall = max(overall, score)

    threats.sort(key=lambda t: t["risk_score"], reverse=True)
    overall_level = risk_level(overall)

    return {
        "overall_risk": overall,
        "risk_level": overall_level,
        "threats": threats,
        "recommendation_set": recommendation_set_for(overall_level),
        "tier_advice": tier_advice(overall_level),
        "weather": {
            "note": "MVP backend - run root uvicorn for Open-Meteo fusion",
        },
        "input_echo": {
            "crop": crop,
            "growth_stage": stage,
            "latitude": req.latitude,
            "longitude": req.longitude,
        },
    }
