"""
Enterprise Dashboard API

Author : Shiva Kumar
Version : 2.1.0
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.dashboard import DashboardSchema
from backend.services.dashboard_service import DashboardService


router = APIRouter(
    prefix="/dashboard",
    tags=["Enterprise Dashboard"],
)

service = DashboardService()


@router.get(
    "/enterprise",
    response_model=DashboardSchema,
)
def get_enterprise_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Return the Enterprise Dashboard for the
    currently authenticated user.
    """

    return service.get_dashboard(
        db,
        user_id=current_user.id,
    )