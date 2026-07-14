from __future__ import annotations

from fastapi import (
    APIRouter,
    Depends,
    File,
    HTTPException,
    UploadFile,
    status,
)

from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.portfolio_live_schema import (
    PortfolioLiveDashboardResponse,
)
from backend.services.portfolio_live_service import (
    PortfolioLiveService,
)


router = APIRouter(
    prefix="/api/portfolio-live",
    tags=["Portfolio Live"],
)


@router.post(
    "/upload",
    response_model=PortfolioLiveDashboardResponse,
)
async def upload_portfolio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        return await PortfolioLiveService.upload(
            user_id=current_user.id,
            file=file,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


@router.get(
    "/dashboard",
    response_model=PortfolioLiveDashboardResponse,
)
def get_portfolio_live_dashboard(
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        return PortfolioLiveService.dashboard(
            user_id=current_user.id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
