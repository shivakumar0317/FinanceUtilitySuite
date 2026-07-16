from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.risk_analytics_schema import RiskAnalyticsDashboardResponse
from backend.services.persistent_upload_service import PersistentUploadService
from backend.services.portfolio_live_service import PortfolioLiveService
from backend.services.web_risk_analytics_service import WebRiskAnalyticsService


router = APIRouter(prefix="/api/risk-analytics", tags=["Risk Analytics"])


@router.get("/dashboard", response_model=RiskAnalyticsDashboardResponse)
def get_risk_analytics_dashboard(
    period: str = Query(default="1y"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    restored = PersistentUploadService.restore_cache(
        db,
        user_id=current_user.id,
        dataset_type=PersistentUploadService.PORTFOLIO_LIVE,
        cache=PortfolioLiveService._portfolios,
        lock=PortfolioLiveService._lock,
    )
    if not restored:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Upload a Portfolio Live file before opening Risk Analytics.",
        )
    try:
        return WebRiskAnalyticsService.dashboard(user_id=current_user.id, period=period)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error
