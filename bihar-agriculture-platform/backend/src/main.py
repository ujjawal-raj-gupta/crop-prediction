from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles

from src.api.routes import router as api_router
from src.core.config import settings


def create_app() -> FastAPI:
    app = FastAPI(title="Bihar Agriculture Platform API", version="1.0.0")

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allow_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def _no_cache_html(request: Request, call_next):
        """Always serve HTML pages with no-store so browsers cannot show
        stale portal markup after we ship new versions. Static assets
        (.css/.js) still use query-string cache-busting and may be cached."""
        response = await call_next(request)
        path = request.url.path
        is_html = path.endswith(".html") or path == "/portal/" or path == "/"
        if is_html:
            response.headers["Cache-Control"] = "no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
        return response

    app.include_router(api_router, prefix="/api/v1")

    web_root = Path(__file__).resolve().parent / "web"
    if web_root.exists():
        # Serve the static portal at /portal and redirect / → /portal/
        app.mount("/portal", StaticFiles(directory=str(web_root), html=True), name="portal")

        @app.get("/")
        def root():
            return RedirectResponse(url="/portal/", status_code=302)

    @app.get("/health")
    def health():
        return {"status": "healthy"}

    return app


app = create_app()

