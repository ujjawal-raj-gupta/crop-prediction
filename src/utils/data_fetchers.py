from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import requests
from tenacity import retry, retry_if_exception_type, stop_after_attempt, wait_exponential_jitter


@dataclass(frozen=True)
class AgmarknetQuery:
    state: str
    commodity: str
    limit: int = 1000
    offset: int = 0


class AgmarknetError(RuntimeError):
    pass


@retry(
    retry=retry_if_exception_type((requests.RequestException, AgmarknetError)),
    wait=wait_exponential_jitter(initial=1, max=10),
    stop=stop_after_attempt(5),
)
def agmarknet_fetch_page(*, api_key: str, resource_id: str, q: AgmarknetQuery) -> dict[str, Any]:
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
    resp = requests.get(url, params=params, timeout=30)
    if resp.status_code >= 400:
        raise AgmarknetError(f"Agmarknet HTTP {resp.status_code}: {resp.text[:500]}")
    data = resp.json()
    if not isinstance(data, dict) or "records" not in data:
        raise AgmarknetError("Unexpected Agmarknet response shape.")
    return data


def agmarknet_fetch_all(*, api_key: str, resource_id: str, state: str, commodity: str) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    offset = 0
    limit = 1000
    while True:
        page = agmarknet_fetch_page(
            api_key=api_key,
            resource_id=resource_id,
            q=AgmarknetQuery(state=state, commodity=commodity, limit=limit, offset=offset),
        )
        records = page.get("records") or []
        if not records:
            break
        out.extend(records)
        offset += len(records)
        if len(records) < limit:
            break
    return out

