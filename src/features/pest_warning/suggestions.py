"""Shared helpers that turn a pest knowledge-base entry into the
suggestion shape consumed by the React frontend and the static portal.

Risk-tier mapping (the contract the UIs depend on):
    LOW    -> show prevention + irrigation tips only (preventive mode)
    MEDIUM -> prevention + organic + chemical + irrigation (treatment mode)
    HIGH   -> all of the above + emergency_actions banner (urgent mode)
"""

from __future__ import annotations

from typing import Any


SUGGESTION_KEYS = (
    "symptoms_list",
    "prevention",
    "organic_solutions",
    "chemical_treatments",
    "irrigation_advice",
    "emergency_actions",
)


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
    """Pull the suggestion arrays out of a KB entry; tolerant of missing keys."""
    return {key: list(entry.get(key) or []) for key in SUGGESTION_KEYS}


def build_threat(
    pest_key: str,
    entry: dict[str, Any],
    *,
    score: int,
    factors: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a single threat payload combining legacy fields with the
    new suggestion arrays.  Callers can include factors / weather context."""
    pretty_name = entry.get("display_name") or pest_key.replace("_", " ").title()
    suggestions = shape_suggestions(entry)
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
        # Legacy fields kept for backwards compatibility
        "symptoms": entry.get("symptoms"),
        "treatment": entry.get("treatment") or {},
        # New rich suggestion arrays
        "suggestions": suggestions,
        "recommendation_set": recommendation_set_for(risk_level(score)),
    }


def tier_advice(level: str) -> dict[str, Any]:
    """Top-level metadata the UI uses to choose banner colour & label."""
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
