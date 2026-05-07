from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Config:
    # Agmarknet / data.gov.in
    AGMARKNET_API_KEY: str = os.getenv("AGMARKNET_API_KEY", "").strip()
    AGMARKNET_RESOURCE_ID: str = os.getenv(
        "AGMARKNET_RESOURCE_ID", "9ef84268-d588-465a-a308-a864a43d0070"
    ).strip()

    # Database (Postgres)
    DATABASE_URL: str = os.getenv("DATABASE_URL", "").strip()

