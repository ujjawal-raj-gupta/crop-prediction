from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_GOV_PORTAL = _PROJECT_ROOT / "gov_portal"
_STATIC_PORTAL = _PROJECT_ROOT / "bihar-agriculture-platform" / "backend" / "src" / "web"

app = FastAPI(title="Bihar Agriculture 4.0 API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api/v1")


@app.get("/")
def root_redirect_to_portal():
    """Opens the government portal; bare `http://host:8001/` was 404 before this redirect."""
    return RedirectResponse(url="/portal/index.html", status_code=302)


@app.get("/health")
def health_check():
    return {"status": "healthy"}

# Government portal UI: use `gov_portal/` only if it has a real `index.html`; empty/placeholder folders fall back to CDN static build.
def _resolve_portal_dir() -> Path | None:
    gov_index = _GOV_PORTAL / "index.html"
    if _GOV_PORTAL.is_dir() and gov_index.is_file():
        return _GOV_PORTAL
    if _STATIC_PORTAL.is_dir() and (_STATIC_PORTAL / "index.html").is_file():
        return _STATIC_PORTAL
    return None


_portal_dir = _resolve_portal_dir()
if _portal_dir:
    app.mount(
        "/portal",
        StaticFiles(directory=str(_portal_dir), html=True),
        name="government_portal",
    )

