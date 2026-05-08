from __future__ import annotations

import os
from dataclasses import dataclass, field


def _env(name: str, default: str = "") -> str:
    return (os.getenv(name) or default).strip()


@dataclass(frozen=True)
class Config:
    # Agmarknet / data.gov.in
    AGMARKNET_API_KEY: str = field(default_factory=lambda: _env("AGMARKNET_API_KEY", ""))
    AGMARKNET_RESOURCE_ID: str = field(
        default_factory=lambda: _env("AGMARKNET_RESOURCE_ID", "9ef84268-d588-465a-a308-a864a43d0070")
    )

    # Database (Postgres)
    DATABASE_URL: str = field(default_factory=lambda: _env("DATABASE_URL", ""))


def load_dotenv_if_present() -> None:
    """
    Optional convenience for local dev:
    reads .env if present (no-op otherwise).
    """
    try:
        from dotenv import load_dotenv

        load_dotenv()
    except Exception:
        pass

