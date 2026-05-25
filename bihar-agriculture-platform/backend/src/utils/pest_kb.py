"""Pest knowledge-base loader + suggestion shaping for the MVP backend.

This module mirrors :mod:`src.features.pest_warning.suggestions` in the
root backend so the MVP returns the same response shape without
cross-stack package imports (both stacks define a top-level ``src``
package which would conflict at import time).

The knowledge-base JSON itself is shared - we read it from the repo
root, with a sane fallback if the file has been moved.
"""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any


SUGGESTION_KEYS = (
    "symptoms_list",
    "prevention",
    "organic_solutions",
    "chemical_treatments",
    "irrigation_advice",
    "emergency_actions",
)


# ---------------------------------------------------------------------- #
# Knowledge-base loader                                                  #
# ---------------------------------------------------------------------- #
def _candidate_kb_paths() -> list[Path]:
    """Locations where the canonical KB JSON might live, in priority order."""
    here = Path(__file__).resolve()
    # ../../../../  -> bihar-agriculture-platform/backend
    backend_root = here.parents[2]
    # ../../../../../  -> bihar-agriculture-platform
    platform_root = here.parents[3]
    # ../../../../../../  -> repo root
    repo_root = here.parents[4]
    return [
        repo_root / "src" / "features" / "pest_warning" / "pest_knowledge_base.json",
        backend_root / "data" / "pest_knowledge_base.json",
        platform_root / "data" / "pest_knowledge_base.json",
    ]


@lru_cache(maxsize=1)
def load_kb() -> dict[str, Any]:
    for path in _candidate_kb_paths():
        if path.is_file():
            try:
                return json.loads(path.read_text(encoding="utf-8"))
            except Exception:
                continue
    return {}


# ---------------------------------------------------------------------- #
# Suggestion shaping helpers                                             #
# ---------------------------------------------------------------------- #
def risk_level(score: float | int) -> str:
    score = float(score or 0)
    if score <= 30:
        return "LOW"
    if score <= 60:
        return "MEDIUM"
    return "HIGH"


def recommendation_set_for(level: str) -> list[str]:
    """Which suggestion sections the UI should render for a given risk tier."""
    level = (level or "LOW").upper()
    if level == "HIGH":
        return [
            "emergency_actions",
            "symptoms_list",
            "chemical_treatments",
            "organic_solutions",
            "irrigation_advice",
            "prevention",
        ]
    if level == "MEDIUM":
        return [
            "symptoms_list",
            "prevention",
            "organic_solutions",
            "chemical_treatments",
            "irrigation_advice",
        ]
    return ["prevention", "symptoms_list", "irrigation_advice"]


def shape_suggestions(entry: dict[str, Any]) -> dict[str, list[str]]:
    return {key: list(entry.get(key) or []) for key in SUGGESTION_KEYS}


def build_threat(
    pest_key: str,
    entry: dict[str, Any],
    *,
    score: int,
    factors: dict[str, Any] | None = None,
) -> dict[str, Any]:
    pretty_name = entry.get("display_name") or pest_key.replace("_", " ").title()
    return {
        "pest_key": pest_key,
        "pest_name": pretty_name,
        "icon": entry.get("icon", "🐛"),
        "category": entry.get("category"),
        "risk_score": int(score),
        "risk_level": risk_level(score),
        "summary": entry.get("summary"),
        "bihar_hotspots": entry.get("bihar_hotspots") or [],
        "factors": factors or {},
        "symptoms": entry.get("symptoms"),
        "treatment": entry.get("treatment") or {},
        "suggestions": shape_suggestions(entry),
        "recommendation_set": recommendation_set_for(risk_level(score)),
    }


def tier_advice(level: str) -> dict[str, Any]:
    level = (level or "LOW").upper()
    if level == "HIGH":
        return {
            "tier": "HIGH",
            "headline": "Immediate action required",
            "tone": "danger",
            "show_emergency_banner": True,
            "show_sections": recommendation_set_for("HIGH"),
        }
    if level == "MEDIUM":
        return {
            "tier": "MEDIUM",
            "headline": "Plan preventive + curative steps",
            "tone": "warning",
            "show_emergency_banner": False,
            "show_sections": recommendation_set_for("MEDIUM"),
        }
    return {
        "tier": "LOW",
        "headline": "Stay watchful; preventive care only",
        "tone": "success",
        "show_emergency_banner": False,
        "show_sections": recommendation_set_for("LOW"),
    }
