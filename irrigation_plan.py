from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
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
    land_acres: float = 1.0
    summary: str = ""


@dataclass(frozen=True)
class ForecastDay:
    day: date
    temp_max_c: float | None
    precip_mm: float
    precip_prob_pct: float | None


# Minutes of irrigation per acre (heuristic demo values).
_MINUTES_PER_ACRE: dict[str, float] = {
    "rice": 55,
    "banana": 50,
    "papaya": 45,
    "watermelon": 40,
    "muskmelon": 40,
    "maize": 35,
    "cotton": 38,
    "jute": 32,
    "orange": 30,
    "pomegranate": 30,
    "mango": 35,
    "grapes": 35,
    "coconut": 40,
}
_DEFAULT_MINUTES_PER_ACRE = 30.0

_DRY_PRECIP_MM = 3.0
_DRY_PRECIP_PROB = 50.0


def _base_interval_hours_for_crop(crop: str) -> float:
    c = (crop or "").strip().lower()
    if c in {"rice", "banana", "papaya", "watermelon", "muskmelon"}:
        return 24.0
    if c in {"maize", "cotton", "jute", "orange", "pomegranate", "mango", "grapes", "coconut"}:
        return 48.0
    if c in {"lentil", "chickpea", "pigeonpeas", "kidneybeans", "mungbean", "mothbeans", "blackgram"}:
        return 72.0
    return 48.0


def _minutes_for_acres(crop: str, land_acres: float) -> int:
    base = _MINUTES_PER_ACRE.get((crop or "").strip().lower(), _DEFAULT_MINUTES_PER_ACRE)
    return max(15, int(round(base * max(0.1, land_acres))))


def _is_dry_day(day: ForecastDay) -> bool:
    if day.precip_mm >= _DRY_PRECIP_MM:
        return False
    if day.precip_prob_pct is not None and day.precip_prob_pct >= _DRY_PRECIP_PROB:
        return False
    return True


def _skip_note(day: ForecastDay) -> str:
    parts = []
    if day.precip_mm >= _DRY_PRECIP_MM:
        parts.append(f"rain forecast {day.precip_mm:.0f} mm")
    if day.precip_prob_pct is not None and day.precip_prob_pct >= _DRY_PRECIP_PROB:
        parts.append(f"{day.precip_prob_pct:.0f}% rain chance")
    reason = ", ".join(parts) if parts else "wet conditions expected"
    return f"Skip — {reason}. Check soil moisture only."


def _irrigate_note(crop: str, land_acres: float, minutes: int, split_hint: str = "") -> str:
    crop_label = (crop or "crop").strip().lower()
    acres_txt = f"{land_acres:g} acre{'s' if land_acres != 1 else ''}"
    base = (
        f"Irrigate {acres_txt} of {crop_label} — about {minutes} min; "
        f"check soil moisture at 15 cm depth."
    )
    if split_hint:
        return f"{base} {split_hint}"
    return base


def build_irrigation_plan(
    *,
    crop: str,
    temperature_c: float,
    humidity_pct: float,
    rainfall_mm: float,
    tz: str = "Asia/Kolkata",
    horizon_events: int = 3,
) -> IrrigationPlan:
    """Legacy demo planner (Flask app)."""
    zone = ZoneInfo(tz)
    now = datetime.now(tz=zone)

    base_h = _base_interval_hours_for_crop(crop)
    temp_adj = -0.5 * max(0.0, min(8.0, temperature_c - 28.0))
    hum_adj = +0.2 * max(0.0, min(30.0, humidity_pct - 60.0))
    rain_adj = +0.3 * max(0.0, min(200.0, rainfall_mm - 100.0))
    interval_h = max(12.0, min(96.0, base_h + temp_adj + hum_adj + rain_adj))

    events: list[IrrigationEvent] = []
    for i in range(horizon_events):
        when = now + timedelta(hours=interval_h * (i + 1))
        note = "Irrigate and check soil moisture (demo plan)."
        events.append(IrrigationEvent(when=when, note=note))

    return IrrigationPlan(crop=crop, tz=tz, events=events)


def build_irrigation_plan_v2(
    *,
    crop: str,
    land_acres: float = 1.0,
    forecast_days: list[ForecastDay],
    tz: str = "Asia/Kolkata",
    max_events: int = 5,
    morning_hour: int = 6,
    morning_minute: int = 30,
) -> IrrigationPlan:
    """
    Forecast-aware irrigation schedule for the Bihar portal.
    Picks dry mornings for irrigation; skips rainy forecast days.
    """
    zone = ZoneInfo(tz)
    acres = max(0.1, min(100.0, float(land_acres)))
    crop_key = (crop or "").strip().lower()
    minutes_total = _minutes_for_acres(crop_key, acres)
    split_hint = ""
    if acres > 5.0:
        split_hint = "Large holding: consider splitting into 2–3 field blocks on the same day."

    events: list[IrrigationEvent] = []
    irrigate_count = 0
    skip_count = 0

    for fd in forecast_days:
        if fd.day < date.today():
            continue

        when = datetime.combine(fd.day, time(morning_hour, morning_minute), tzinfo=zone)
        if when <= datetime.now(tz=zone):
            when = datetime.now(tz=zone) + timedelta(hours=2)
            when = when.replace(minute=morning_minute, second=0, microsecond=0)

        if _is_dry_day(fd):
            if irrigate_count >= max_events:
                continue
            events.append(
                IrrigationEvent(
                    when=when,
                    note=_irrigate_note(crop_key, acres, minutes_total, split_hint),
                )
            )
            irrigate_count += 1
        else:
            events.append(IrrigationEvent(when=when, note=_skip_note(fd)))
            skip_count += 1

        if irrigate_count >= max_events and len(events) >= max_events + 2:
            break

    # Fallback if forecast had no usable days
    if irrigate_count == 0:
        now = datetime.now(tz=zone)
        interval_h = _base_interval_hours_for_crop(crop_key)
        for i in range(min(3, max_events)):
            when = now + timedelta(hours=interval_h * (i + 1))
            events.append(
                IrrigationEvent(
                    when=when,
                    note=_irrigate_note(crop_key, acres, minutes_total),
                )
            )
        irrigate_count = min(3, max_events)
        summary = (
            f"{irrigate_count} session(s) for {acres:g} acres (seasonal fallback — "
            f"weather forecast unavailable)."
        )
    else:
        summary = (
            f"{irrigate_count} irrigation session(s) planned for {acres:g} acres of {crop_key}; "
            f"{skip_count} day(s) skipped due to rain in the forecast."
        )

    return IrrigationPlan(
        crop=crop_key,
        tz=tz,
        events=events[: max_events + 3],
        land_acres=acres,
        summary=summary,
    )


def plan_to_api_dict(plan: IrrigationPlan, *, weather_source: str = "open-meteo") -> dict:
    zone = ZoneInfo(plan.tz)
    events_out = []
    for ev in plan.events:
        local = ev.when.astimezone(zone)
        events_out.append(
            {
                "when_local": local.strftime("%Y-%m-%d %I:%M %p"),
                "when_iso": local.isoformat(),
                "note": ev.note,
            }
        )
    return {
        "crop": plan.crop,
        "land_acres": plan.land_acres,
        "tz": plan.tz,
        "weather_source": weather_source,
        "summary": plan.summary,
        "events": events_out,
    }
