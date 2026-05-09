from __future__ import annotations

# Known Bihar mandi keywords we target (substring match against API "market" text).
BIHAR_MANDIS = [
    "patna",
    "muzaffarpur",
    "bhagalpur",
    "darbhanga",
    "gaya",
    "begusarai",
]


def match_bihar_mandi_key(market_raw: str | None) -> str | None:
    """
    Map free-text market names from Agmarknet (e.g. "Patna Anaj Mandi") to a canonical key.
    """
    s = (market_raw or "").strip().lower()
    if not s:
        return None
    for m in BIHAR_MANDIS:
        if len(m) >= 4 and m in s:
            return m
        if m == s:
            return m
    return None


def commodity_matches_crop(*, record_commodity: str, crop_norm: str) -> bool:
    """
    Agmarknet commodity labels vary (e.g. 'Raw Jute' vs model label 'jute').
    """
    a = (record_commodity or "").strip().lower()
    b = (crop_norm or "").strip().lower()
    if not a or not b:
        return False
    if a == b:
        return True
    if len(b) >= 3 and b in a:
        return True
    if len(a) >= 3 and a in b:
        return True
    return False
