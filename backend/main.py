from __future__ import annotations

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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


settings = get_settings()
logger = logging.getLogger("finance_utility_suite")

app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(system_router)
app.include_router(auth_router)
app.include_router(portfolio_router)
app.include_router(analytics_router)
app.include_router(market_router)
app.include_router(market_dashboard_router)
app.include_router(watchlist_router)
app.include_router(stock_router)
app.include_router(portfolio_live_router)
app.include_router(risk_analytics_router)
app.include_router(mtf_router)


@app.on_event("startup")
def startup_diagnostics() -> None:
    database_status = "Connected"

    try:
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
    except Exception:
        database_status = "Unavailable"
        logger.exception("Database startup check failed.")

    logger.info(
        "\n"
        "=========================================\n"
        " %s\n"
        " Version     : %s\n"
        " Environment : %s\n"
        " Database    : %s\n"
        "=========================================",
        settings.app_name,
        settings.app_version,
        settings.environment,
        database_status,
    )
