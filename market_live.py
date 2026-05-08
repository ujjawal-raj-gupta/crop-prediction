from __future__ import annotations

import json
import os
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import desc, select

from src.db.models import Base, PriceHistory
from src.db.session import engine, session_scope
from src.utils.config import Config, load_dotenv_if_present
from src.utils.data_fetchers import AgmarknetError, AgmarknetQuery, agmarknet_fetch_page


BIHAR_MANDIS = [
    "patna",
    "muzaffarpur",
    "bhagalpur",
    "darbhanga",
    "gaya",
    "begusarai",
]

SNAPSHOT_PATH = str(Path(__file__).resolve().parent / "data" / "agmarknet_snapshot.json")


def ensure_market_tables() -> None:
    Base.metadata.create_all(bind=engine)


def _parse_date_iso(s: str) -> str | None:
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def _num(x: Any) -> float | None:
    try:
        return float(str(x).strip())
    except Exception:
        return None


@dataclass(frozen=True)
class LiveMandiPrice:
    crop: str
    mandi: str
    district: str | None
    state: str
    date: str
    modal_price_per_quintal: float | None
    min_price: float | None
    max_price: float | None


def _upsert_prices_from_agmarknet(*, crop: str, state: str, mandis: list[str]) -> int:
    # Allow local dev via .env without needing to export env vars every terminal session.
    load_dotenv_if_present()
    cfg = Config()
    # For UI usage we only need a small slice; fetching all pages can time out.
    page = agmarknet_fetch_page(
        api_key=cfg.AGMARKNET_API_KEY,
        resource_id=cfg.AGMARKNET_RESOURCE_ID,
        q=AgmarknetQuery(state=state, commodity=crop, limit=250, offset=0),
        timeout_s=30.0,
        max_attempts=2,
    )
    records = page.get("records") or []
    if not records:
        return 0

    inserted_or_updated = 0
    for r in records:
        date_iso = _parse_date_iso(str(r.get("arrival_date") or r.get("date") or ""))
        mandi = str(r.get("market") or r.get("mandi") or "").strip().lower()
        if not date_iso or not mandi or mandi not in mandis:
            continue

        district = (str(r.get("district") or "").strip().lower() or None)
        modal = _num(r.get("modal_price"))
        minp = _num(r.get("min_price"))
        maxp = _num(r.get("max_price"))

        payload = dict(
            date=date_iso,
            crop=crop.strip().lower(),
            mandi=mandi,
            state=state.strip().lower(),
            district=district,
            price_per_quintal=modal,
            min_price=minp,
            max_price=maxp,
            raw=json.loads(json.dumps(r)),
        )

        with session_scope() as s:
            existing = s.execute(
                select(PriceHistory).where(
                    PriceHistory.date == date_iso,
                    PriceHistory.crop == payload["crop"],
                    PriceHistory.mandi == payload["mandi"],
                    PriceHistory.state == payload["state"],
                )
            ).scalar_one_or_none()

            if existing is None:
                s.add(PriceHistory(**payload))
            else:
                for k, v in payload.items():
                    setattr(existing, k, v)
            inserted_or_updated += 1

    return inserted_or_updated


def _try_import_snapshot_into_db(*, crop_norm: str, state_norm: str, mandis: list[str]) -> bool:
    """
    Imports data/agmarknet_snapshot.json (if present) into price_history for offline usage.
    Returns True if anything was inserted/updated.
    """
    path = os.path.abspath(SNAPSHOT_PATH)
    if not os.path.exists(path):
        return False
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except Exception:
        return False

    records = payload.get("records") if isinstance(payload, dict) else None
    if not isinstance(records, list) or not records:
        return False

    inserted_or_updated = 0
    for r in records:
        commodity = str(r.get("commodity") or "").strip().lower()
        mandi = str(r.get("market") or r.get("mandi") or "").strip().lower()
        state = str(r.get("state") or state_norm).strip().lower()
        if commodity != crop_norm or state != state_norm or mandi not in mandis:
            continue

        date_iso = _parse_date_iso(str(r.get("arrival_date") or r.get("date") or ""))
        if not date_iso:
            continue

        district = (str(r.get("district") or "").strip().lower() or None)
        modal = _num(r.get("modal_price"))
        minp = _num(r.get("min_price"))
        maxp = _num(r.get("max_price"))

        payload_row = dict(
            date=date_iso,
            crop=crop_norm,
            mandi=mandi,
            state=state_norm,
            district=district,
            price_per_quintal=modal,
            min_price=minp,
            max_price=maxp,
            raw=json.loads(json.dumps(r)),
        )

        with session_scope() as s:
            existing = s.execute(
                select(PriceHistory).where(
                    PriceHistory.date == date_iso,
                    PriceHistory.crop == crop_norm,
                    PriceHistory.mandi == mandi,
                    PriceHistory.state == state_norm,
                )
            ).scalar_one_or_none()
            if existing is None:
                s.add(PriceHistory(**payload_row))
            else:
                for k, v in payload_row.items():
                    setattr(existing, k, v)
            inserted_or_updated += 1

    return inserted_or_updated > 0


def get_live_mandi_prices(
    *,
    crop_label: str,
    state: str = "Bihar",
    mandis: list[str] | None = None,
    max_age_days: int = 2,
) -> tuple[list[LiveMandiPrice], str | None]:
    """
    Returns (prices, error). If AGMARKNET_API_KEY isn't configured, prices will be empty with an error message.
    """
    ensure_market_tables()

    mandis = mandis or BIHAR_MANDIS
    crop_api = crop_label.strip()
    if not crop_api:
        return [], "Missing crop."

    # Agmarknet commodity names are typically Title Case.
    commodity = crop_api.strip().title()
    crop_norm = crop_api.strip().lower()
    state_norm = state.strip().lower()

    # Check if we already have recent data (for any mandi).
    cutoff = (date.today() - timedelta(days=max_age_days)).isoformat()
    with session_scope() as s:
        recent = s.execute(
            select(PriceHistory)
            .where(
                PriceHistory.crop == crop_norm,
                PriceHistory.state == state_norm,
                PriceHistory.mandi.in_(mandis),
                PriceHistory.date >= cutoff,
            )
            .order_by(desc(PriceHistory.date))
            .limit(1)
        ).scalar_one_or_none()

    if recent is None:
        # First try offline snapshot (populated by GitHub Actions).
        if _try_import_snapshot_into_db(crop_norm=crop_norm, state_norm=state_norm, mandis=mandis):
            # Re-check recent after import
            with session_scope() as s:
                recent = s.execute(
                    select(PriceHistory)
                    .where(
                        PriceHistory.crop == crop_norm,
                        PriceHistory.state == state_norm,
                        PriceHistory.mandi.in_(mandis),
                        PriceHistory.date >= cutoff,
                    )
                    .order_by(desc(PriceHistory.date))
                    .limit(1)
                ).scalar_one_or_none()

        # Still nothing? Avoid blocking the prediction request on slow upstream APIs.
        # If you want auto-fetch on each prediction, set AGMARKNET_AUTO_FETCH=1.
        if recent is None and (os.getenv("AGMARKNET_AUTO_FETCH") or "").strip() != "1":
            return (
                [],
                "No cached Agmarknet prices yet for this crop. Enable GitHub Actions snapshot, "
                "or run scripts/agmarknet_ingest.py once to populate the database (or set AGMARKNET_AUTO_FETCH=1).",
            )
        try:
            _upsert_prices_from_agmarknet(crop=commodity, state=state, mandis=mandis)
        except AgmarknetError as e:
            return [], str(e)
        except Exception:
            return [], "Failed to fetch live market prices."

    # Return the latest row per mandi
    out: list[LiveMandiPrice] = []
    with session_scope() as s:
        rows = s.execute(
            select(PriceHistory)
            .where(
                PriceHistory.crop == crop_norm,
                PriceHistory.state == state_norm,
                PriceHistory.mandi.in_(mandis),
            )
            .order_by(desc(PriceHistory.date))
            .limit(200)
        ).scalars()

        seen: set[str] = set()
        for r in rows:
            if r.mandi in seen:
                continue
            seen.add(r.mandi)
            out.append(
                LiveMandiPrice(
                    crop=str(r.crop),
                    mandi=str(r.mandi),
                    district=str(r.district) if r.district else None,
                    state=str(r.state),
                    date=str(r.date),
                    modal_price_per_quintal=float(r.price_per_quintal) if r.price_per_quintal is not None else None,
                    min_price=float(r.min_price) if r.min_price is not None else None,
                    max_price=float(r.max_price) if r.max_price is not None else None,
                )
            )

    out.sort(key=lambda x: (x.mandi,))
    return out, None

