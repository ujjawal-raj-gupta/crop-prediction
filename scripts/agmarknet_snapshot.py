from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.config import Config, load_dotenv_if_present
from src.utils.data_fetchers import AgmarknetError, AgmarknetQuery, agmarknet_fetch_page


OUT_PATH = PROJECT_ROOT / "data" / "agmarknet_snapshot.json"


DEFAULT_COMMODITIES = [
    "Wheat",
    "Rice",
    "Maize",
    "Jute",
    "Banana",
    "Mango",
    "Potato",
    "Onion",
]


BIHAR_MANDIS = [
    "patna",
    "muzaffarpur",
    "bhagalpur",
    "darbhanga",
    "gaya",
    "begusarai",
]


def main() -> None:
    load_dotenv_if_present()
    cfg = Config()

    state = (os.getenv("AG_STATE") or "Bihar").strip()
    limit = int(float(os.getenv("AG_LIMIT", "250")))
    timeout_s = float(os.getenv("AG_TIMEOUT_S", "30"))

    commodities_raw = (os.getenv("AG_COMMODITIES") or "").strip()
    commodities = (
        [c.strip() for c in commodities_raw.split(",") if c.strip()]
        if commodities_raw
        else DEFAULT_COMMODITIES
    )

    all_rows: list[dict] = []
    fetch_errors: list[dict[str, str]] = []
    max_attempts = int(float(os.getenv("AG_MAX_ATTEMPTS", "2")))

    for commodity in commodities:
        try:
            page = agmarknet_fetch_page(
                api_key=cfg.AGMARKNET_API_KEY,
                resource_id=cfg.AGMARKNET_RESOURCE_ID,
                q=AgmarknetQuery(state=state, commodity=commodity, limit=limit, offset=0),
                timeout_s=timeout_s,
                max_attempts=max_attempts,
            )
            records = page.get("records") or []
            for r in records:
                mandi = str(r.get("market") or r.get("mandi") or "").strip().lower()
                if mandi and mandi in BIHAR_MANDIS:
                    all_rows.append(r)
            print(f"OK commodity={commodity!r} mandi_rows_so_far={len(all_rows)}")
        except AgmarknetError as e:
            msg = str(e)
            fetch_errors.append({"commodity": commodity, "error": msg})
            print(f"WARN commodity={commodity!r}: {msg}")
        except Exception as e:
            msg = str(e)
            fetch_errors.append({"commodity": commodity, "error": msg})
            print(f"WARN commodity={commodity!r}: {msg}")

    payload = {
        "source": "data.gov.in (Agmarknet)",
        "resource_id": cfg.AGMARKNET_RESOURCE_ID,
        "state": state,
        "mandis": BIHAR_MANDIS,
        "commodities": commodities,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "records": all_rows,
        "fetch_errors": fetch_errors,
    }

    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    print("Wrote:", OUT_PATH)
    print("Records:", len(all_rows))
    if fetch_errors:
        print("Fetch errors:", len(fetch_errors))
    # Do not fail the workflow if some commodities time out; snapshot still useful.
    if not all_rows and fetch_errors:
        print("NOTE: No mandi rows matched yet; check fetch_errors in JSON or commodity spellings.")


if __name__ == "__main__":
    main()

