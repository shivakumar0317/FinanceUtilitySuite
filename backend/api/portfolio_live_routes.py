from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.portfolio_live_schema import PortfolioLiveDashboardResponse
from backend.schemas.upload_dataset_schema import UploadHistoryItem
from backend.services.persistent_upload_service import PersistentUploadService
from backend.services.portfolio_live_service import PortfolioLiveService


router = APIRouter(prefix="/api/portfolio-live", tags=["Portfolio Live"])


def _restore(db: Session, user_id: int) -> bool:
    return PersistentUploadService.restore_cache(
        db,
        user_id=user_id,
        dataset_type=PersistentUploadService.PORTFOLIO_LIVE,
        cache=PortfolioLiveService._portfolios,
        lock=PortfolioLiveService._lock,
    )


@router.post("/upload", response_model=PortfolioLiveDashboardResponse)
async def upload_portfolio(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = await PortfolioLiveService.upload(user_id=current_user.id, file=file)
        with PortfolioLiveService._lock:
            dataframe = PortfolioLiveService._portfolios[current_user.id].copy()

        PersistentUploadService.save_dataframe(
            db,
            user_id=current_user.id,
            dataset_type=PersistentUploadService.PORTFOLIO_LIVE,
            filename=file.filename or "portfolio-upload",
            content_type=file.content_type,
            dataframe=dataframe,
        )
        return result
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.get("/dashboard", response_model=PortfolioLiveDashboardResponse)
def get_portfolio_live_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if not _restore(db, current_user.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No saved Portfolio Live upload was found.",
        )
    return PortfolioLiveService.dashboard(user_id=current_user.id)


@router.get("/uploads", response_model=list[UploadHistoryItem])
def portfolio_upload_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PersistentUploadService.list_history(
        db,
        user_id=current_user.id,
        dataset_type=PersistentUploadService.PORTFOLIO_LIVE,
    )


@router.post("/uploads/{upload_id}/activate", response_model=PortfolioLiveDashboardResponse)
def activate_portfolio_upload(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        PersistentUploadService.activate(
            db,
            user_id=current_user.id,
            dataset_type=PersistentUploadService.PORTFOLIO_LIVE,
            upload_id=upload_id,
        )
        PersistentUploadService.clear_cache(
            user_id=current_user.id,
            cache=PortfolioLiveService._portfolios,
            lock=PortfolioLiveService._lock,
        )
        _restore(db, current_user.id)
        return PortfolioLiveService.dashboard(user_id=current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/uploads/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_portfolio_upload(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    try:
        PersistentUploadService.delete(
            db,
            user_id=current_user.id,
            dataset_type=PersistentUploadService.PORTFOLIO_LIVE,
            upload_id=upload_id,
        )
        PersistentUploadService.clear_cache(
            user_id=current_user.id,
            cache=PortfolioLiveService._portfolios,
            lock=PortfolioLiveService._lock,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
