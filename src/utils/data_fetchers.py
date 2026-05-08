from __future__ import annotations

from dataclasses import dataclass
import time
from typing import Any

import requests


@dataclass(frozen=True)
class AgmarknetQuery:
    state: str
    commodity: str
    limit: int = 1000
    offset: int = 0


class AgmarknetError(RuntimeError):
    pass


def agmarknet_fetch_page(
    *,
    api_key: str,
    resource_id: str,
    q: AgmarknetQuery,
    timeout_s: float = 15.0,
    max_attempts: int = 2,
) -> dict[str, Any]:
    if not api_key:
        raise AgmarknetError("Missing AGMARKNET_API_KEY.")

    url = f"https://api.data.gov.in/resource/{resource_id}"
    params = {
        "api-key": api_key,
        "format": "json",
        "limit": q.limit,
        "offset": q.offset,
        "filters[state]": q.state,
        "filters[commodity]": q.commodity,
    }
    last_err: Exception | None = None
    attempts = max(1, int(max_attempts))
    for i in range(attempts):
        try:
            resp = requests.get(url, params=params, timeout=timeout_s)
            if resp.status_code >= 400:
                raise AgmarknetError(f"Agmarknet HTTP {resp.status_code}: {resp.text[:500]}")
            data = resp.json()
            if not isinstance(data, dict) or "records" not in data:
                raise AgmarknetError("Unexpected Agmarknet response shape.")
            return data
        except (requests.RequestException, AgmarknetError, ValueError) as e:
            last_err = e
            # small backoff to avoid immediate hammering
            if i < attempts - 1:
                time.sleep(min(1.0 + (2**i) * 0.5, 5.0))
            continue

    assert last_err is not None
    raise AgmarknetError(str(last_err))


def agmarknet_fetch_all(
    *,
    api_key: str,
    resource_id: str,
    state: str,
    commodity: str,
    timeout_s: float = 15.0,
    max_attempts: int = 2,
) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    offset = 0
    limit = 1000
    while True:
        page = agmarknet_fetch_page(
            api_key=api_key,
            resource_id=resource_id,
            q=AgmarknetQuery(state=state, commodity=commodity, limit=limit, offset=offset),
            timeout_s=timeout_s,
            max_attempts=max_attempts,
        )
        records = page.get("records") or []
        if not records:
            break
        out.extend(records)
        offset += len(records)
        if len(records) < limit:
            break
    return out

