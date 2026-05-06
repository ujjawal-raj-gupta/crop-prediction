from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


@dataclass(frozen=True)
class IrrigationEvent:
    when: datetime
    note: str


@dataclass(frozen=True)
class IrrigationPlan:
    crop: str
    tz: str
    events: list[IrrigationEvent]


def _base_interval_hours_for_crop(crop: str) -> float:
    """
    Rough heuristic intervals. This is not agronomic advice; it's a demo schedule.
    """
    c = (crop or "").strip().lower()
    # More frequent
    if c in {"rice", "banana", "papaya", "watermelon", "muskmelon"}:
        return 24.0
    # Medium
    if c in {"maize", "cotton", "jute", "orange", "pomegranate", "mango", "grapes", "coconut"}:
        return 48.0
    # Less frequent (many pulses)
    if c in {"lentil", "chickpea", "pigeonpeas", "kidneybeans", "mungbean", "mothbeans", "blackgram"}:
        return 72.0
    return 48.0


def build_irrigation_plan(
    *,
    crop: str,
    temperature_c: float,
    humidity_pct: float,
    rainfall_mm: float,
    tz: str = "Asia/Kolkata",
    horizon_events: int = 3,
) -> IrrigationPlan:
    """
    Build a simple timing plan for demo purposes.
    - Higher temp -> irrigate a bit sooner
    - Higher humidity -> irrigate a bit later
    - High rainfall -> postpone irrigation
    """
    zone = ZoneInfo(tz)
    now = datetime.now(tz=zone)

    base_h = _base_interval_hours_for_crop(crop)

    # Adjustments (bounded)
    temp_adj = -0.5 * max(0.0, min(8.0, temperature_c - 28.0))  # up to -4 hours
    hum_adj = +0.2 * max(0.0, min(30.0, humidity_pct - 60.0))   # up to +6 hours
    rain_adj = +0.3 * max(0.0, min(200.0, rainfall_mm - 100.0))  # up to +60 hours

    interval_h = max(12.0, min(96.0, base_h + temp_adj + hum_adj + rain_adj))

    events: list[IrrigationEvent] = []
    for i in range(horizon_events):
        when = now + timedelta(hours=interval_h * (i + 1))
        note = "Irrigate and check soil moisture (demo plan)."
        events.append(IrrigationEvent(when=when, note=note))

    return IrrigationPlan(crop=crop, tz=tz, events=events)

