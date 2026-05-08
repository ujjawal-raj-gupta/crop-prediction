from __future__ import annotations

import json
import os
from datetime import datetime

import sys
from pathlib import Path

from sqlalchemy import select

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import Config
from src.utils.config import load_dotenv_if_present
from src.utils.data_fetchers import AgmarknetQuery, agmarknet_fetch_page
from src.db.models import PriceHistory
from src.db.session import session_scope


def _parse_date(s: str) -> str | None:
    s = (s or "").strip()
    if not s:
        return None
    for fmt in ("%d/%m/%Y", "%Y-%m-%d"):
        try:
            return datetime.strptime(s, fmt).date().isoformat()
        except ValueError:
            continue
    return None


def main() -> None:
    load_dotenv_if_present()
    cfg = Config()

    state = os.getenv("AG_STATE", "Bihar")
    commodity = os.getenv("AG_COMMODITY", "Wheat")

    # data.gov.in can be slow/unreliable; ingest in small pages to avoid long hangs.
    limit = int(float(os.getenv("AG_LIMIT", "250")))
    max_pages = int(float(os.getenv("AG_MAX_PAGES", "1")))
    timeout_s = float(os.getenv("AG_TIMEOUT_S", "60"))

    records: list[dict] = []
    offset = 0
    for _ in range(max_pages):
        page = agmarknet_fetch_page(
            api_key=cfg.AGMARKNET_API_KEY,
            resource_id=cfg.AGMARKNET_RESOURCE_ID,
            q=AgmarknetQuery(state=state, commodity=commodity, limit=limit, offset=offset),
            timeout_s=timeout_s,
            max_attempts=2,
        )
        recs = page.get("records") or []
        if not recs:
            break
        records.extend(recs)
        offset += len(recs)
        if len(recs) < limit:
            break

    if not records:
        print("No records returned.")
        return

    # Normalize common columns (Agmarknet fields vary; keep raw JSON)
    # Common keys observed: arrival_date, market, district, modal_price, min_price, max_price, commodity, state
    inserted = 0
    updated = 0
    for r in records:
        date_iso = _parse_date(str(r.get("arrival_date") or r.get("date") or ""))
        mandi = str(r.get("market") or r.get("mandi") or "").strip().lower()
        district = (str(r.get("district") or "").strip().lower() or None)

        def _num(x):
            try:
                return float(str(x).strip())
            except Exception:
                return None

        modal = _num(r.get("modal_price"))
        minp = _num(r.get("min_price"))
        maxp = _num(r.get("max_price"))

        if not date_iso or not mandi:
            continue

        # Use ORM UPSERT pattern (portable across sqlite/postgres):
        # - check if row exists
        # - insert or update
        with session_scope() as s:
            existing = s.execute(
                select(PriceHistory).where(
                    PriceHistory.date == date_iso,
                    PriceHistory.crop == commodity.lower(),
                    PriceHistory.mandi == mandi,
                    PriceHistory.state == state.lower(),
                )
            ).scalar_one_or_none()

            payload = dict(
                date=date_iso,
                crop=commodity.lower(),
                mandi=mandi,
                state=state.lower(),
                district=district,
                price_per_quintal=modal,
                min_price=minp,
                max_price=maxp,
                raw=json.loads(json.dumps(r)),  # ensure JSON-serializable
            )

            if existing is None:
                s.add(PriceHistory(**payload))
                inserted += 1
            else:
                for k, v in payload.items():
                    setattr(existing, k, v)
                updated += 1

    print(f"Inserted: {inserted}, Updated: {updated} for {state=} {commodity=}")


if __name__ == "__main__":
    main()

