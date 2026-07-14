from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status

from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.risk_analytics_schema import RiskAnalyticsDashboardResponse
from backend.services.web_risk_analytics_service import WebRiskAnalyticsService


router = APIRouter(prefix="/api/risk-analytics", tags=["Risk Analytics"])


@router.get("/dashboard", response_model=RiskAnalyticsDashboardResponse)
def get_risk_analytics_dashboard(
    period: str = Query(default="1y"),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        return WebRiskAnalyticsService.dashboard(
            user_id=current_user.id,
            period=period,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error
