from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import backend.models  # noqa: F401
from backend.api.auth_routes import router as auth_router
from backend.api.market_routes import router as market_router
from backend.api.portfolio_routes import router as portfolio_router
from backend.config import get_settings
from backend.database import Base, engine
from backend.api.analytics_routes import router as analytics_router
from backend.api.market_dashboard_routes import (
    router as market_dashboard_router,
)
from backend.api.watchlist_routes import (
    router as watchlist_router,
)
from backend.api.stock_routes import router as stock_router
from backend.api.portfolio_live_routes import (
        router as portfolio_live_router,
)


settings = get_settings()

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    version="1.5.2",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(portfolio_router)
app.include_router(market_router)
app.include_router(analytics_router)
app.include_router(market_dashboard_router)
app.include_router(watchlist_router)
app.include_router(stock_router)
app.include_router(portfolio_live_router)


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "ok",
        "application": settings.app_name,
        "version": "1.5.2",
    }
