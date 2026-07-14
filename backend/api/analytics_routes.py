from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.analytics_schema import AnalyticsDashboardResponse
from backend.services.analytics_service import AnalyticsService

router = APIRouter(prefix='/api/analytics', tags=['Analytics'])


@router.get('/dashboard', response_model=AnalyticsDashboardResponse)
def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return AnalyticsService.dashboard(db=db, current_user=current_user)
