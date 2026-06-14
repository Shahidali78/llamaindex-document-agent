"""FastAPI application entrypoint."""

from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.db.database import init_db
from app.routes import auth, chat, documents, extraction, health, reports, usage
from app.security import require_api_key, track_usage
from app.utils.logger import get_logger

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings.ensure_dirs()
    init_db()
    logger.info("%s started (env=%s)", settings.app_name, settings.environment)
    if not settings.openai_api_key:
        logger.warning("OPENAI_API_KEY is not set. AI endpoints will return 503 until configured.")
    if settings.auth_enabled:
        logger.info("Auth ENABLED: data/AI endpoints require an 'X-API-Key' header.")
        if not settings.api_key_list and not settings.admin_api_token:
            logger.warning(
                "Auth is enabled but no API_KEYS and no ADMIN_API_TOKEN are set — "
                "no requests can authenticate. Set one of them."
            )
    else:
        logger.warning("Auth is DISABLED. All endpoints are open.")
    yield
    logger.info("%s shutting down", settings.app_name)


app = FastAPI(
    title=settings.app_name,
    description="SaaS-style document intelligence platform powered by LlamaIndex.",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# Public endpoints.
app.include_router(health.router)
# Admin-protected key management (guarded inside the router).
app.include_router(auth.router)

# Data / AI endpoints require a valid API key (when auth is enabled) and have
# their usage recorded per key.
protected = [Depends(require_api_key), Depends(track_usage)]
app.include_router(documents.router, dependencies=protected)
app.include_router(chat.router, dependencies=protected)
app.include_router(extraction.router, dependencies=protected)
app.include_router(reports.router, dependencies=protected)
app.include_router(usage.router, dependencies=protected)


@app.get("/", tags=["root"])
def root() -> dict:
    return {
        "name": settings.app_name,
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
    }
