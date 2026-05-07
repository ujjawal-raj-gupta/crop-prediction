from __future__ import annotations

import json
import os
from datetime import datetime

import pandas as pd
import psycopg2
from psycopg2.extras import execute_values

from src.utils.config import Config
from src.utils.data_fetchers import agmarknet_fetch_all


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
    cfg = Config()
    if not cfg.DATABASE_URL:
        raise RuntimeError("Missing DATABASE_URL (Postgres connection string).")

    state = os.getenv("AG_STATE", "Bihar")
    commodity = os.getenv("AG_COMMODITY", "Wheat")

    records = agmarknet_fetch_all(
        api_key=cfg.AGMARKNET_API_KEY,
        resource_id=cfg.AGMARKNET_RESOURCE_ID,
        state=state,
        commodity=commodity,
    )
    if not records:
        print("No records returned.")
        return

    df = pd.DataFrame(records)

    # Normalize common columns (Agmarknet fields vary; keep raw JSON)
    # Common keys observed: arrival_date, market, district, modal_price, min_price, max_price, commodity, state
    rows = []
    for r in records:
        date = _parse_date(str(r.get("arrival_date") or r.get("date") or ""))
        mandi = str(r.get("market") or r.get("mandi") or "").strip()
        district = str(r.get("district") or "").strip() or None

        def _num(x):
            try:
                return float(str(x).strip())
            except Exception:
                return None

        modal = _num(r.get("modal_price"))
        minp = _num(r.get("min_price"))
        maxp = _num(r.get("max_price"))

        if not date or not mandi:
            continue

        rows.append(
            (
                date,
                commodity.lower(),
                mandi.lower(),
                state.lower(),
                district.lower() if district else None,
                modal,
                minp,
                maxp,
                json.dumps(r),
            )
        )

    if not rows:
        print("No usable rows after normalization.")
        return

    conn = psycopg2.connect(cfg.DATABASE_URL)
    try:
        with conn:
            with conn.cursor() as cur:
                execute_values(
                    cur,
                    """
                    INSERT INTO price_history
                      (date, crop, mandi, state, district, price_per_quintal, min_price, max_price, raw)
                    VALUES %s
                    ON CONFLICT (date, crop, mandi, state) DO UPDATE SET
                      district = EXCLUDED.district,
                      price_per_quintal = EXCLUDED.price_per_quintal,
                      min_price = EXCLUDED.min_price,
                      max_price = EXCLUDED.max_price,
                      raw = EXCLUDED.raw
                    """,
                    rows,
                    page_size=1000,
                )
        print(f"Inserted/updated rows: {len(rows)} for {state=} {commodity=}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()

