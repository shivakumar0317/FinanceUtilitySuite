from __future__ import annotations
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from sqlalchemy import text

import backend.models  # noqa: F401
from backend.api.analytics_routes import router as analytics_router
from backend.api.auth_routes import router as auth_router
from backend.api.market_dashboard_routes import router as market_dashboard_router
from backend.api.market_routes import router as market_router
from backend.api.mtf_routes import router as mtf_router
from backend.api.portfolio_live_routes import router as portfolio_live_router
from backend.api.portfolio_routes import router as portfolio_router
from backend.api.risk_analytics_routes import router as risk_analytics_router
from backend.api.stock_routes import router as stock_router
from backend.api.system_routes import router as system_router
from backend.api.watchlist_routes import router as watchlist_router
from backend.config import get_settings
from backend.database import SessionLocal
from backend.exceptions import register_exception_handlers
from backend.logging_config import configure_logging
from backend.middleware.request_id import RequestIDMiddleware
from backend.middleware.request_logger import RequestLoggingMiddleware
from backend.middleware.response_time import ResponseTimeMiddleware
from backend.performance_settings import get_performance_settings
from backend.utils.cache import configure_cache, get_cache

settings = get_settings()
performance = get_performance_settings()
configure_logging(logging.DEBUG if settings.debug else logging.INFO)
logger = logging.getLogger("finance_utility_suite")

app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
if performance.gzip_enabled:
    app.add_middleware(GZipMiddleware, minimum_size=performance.gzip_minimum_size, compresslevel=performance.gzip_compresslevel)
app.add_middleware(ResponseTimeMiddleware)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RequestIDMiddleware)
register_exception_handlers(app)

for router in (
    system_router, auth_router, portfolio_router, analytics_router,
    market_router, market_dashboard_router, watchlist_router, stock_router,
    portfolio_live_router, risk_analytics_router, mtf_router,
):
    app.include_router(router)

@app.on_event("startup")
def startup_diagnostics() -> None:
    database_status = "Connected"
    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        database_status = "Unavailable"
        logger.exception("Database startup check failed.")

    configure_cache(
        enabled=performance.cache_enabled,
        default_ttl=performance.cache_default_ttl,
        max_entries=performance.cache_max_entries,
    )
    logger.info(
        "Application started | name=%s | version=%s | environment=%s | database=%s | cache_enabled=%s | cache_ttl=%s | gzip_enabled=%s",
        settings.app_name, settings.app_version, settings.environment, database_status,
        performance.cache_enabled, performance.cache_default_ttl, performance.gzip_enabled,
    )

@app.on_event("shutdown")
def shutdown_diagnostics() -> None:
    get_cache().clear()
    logger.info("Application stopped | name=%s | version=%s", settings.app_name, settings.app_version)
