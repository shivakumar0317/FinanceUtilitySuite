from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.mtf_schema import ClientRiskItem, MTFDashboardResponse, SymbolExposureItem
from backend.schemas.upload_dataset_schema import UploadHistoryItem
from backend.services.persistent_upload_service import PersistentUploadService
from backend.services.web_mtf_service import WebMTFService


router = APIRouter(prefix="/api/mtf", tags=["MTF Dashboard"])


def _restore(db: Session, user_id: int) -> bool:
    restored = PersistentUploadService.restore_cache(
        db,
        user_id=user_id,
        dataset_type=PersistentUploadService.MTF,
        cache=WebMTFService._datasets,
        lock=WebMTFService._lock,
    )

    if not restored:
        return False

    with WebMTFService._lock:
        dataframe = WebMTFService._datasets[user_id].copy()

    enriched = WebMTFService._enrich_cap_category(dataframe)

    with WebMTFService._lock:
        WebMTFService._datasets[user_id] = enriched

    return True


@router.post("/upload", response_model=MTFDashboardResponse)
async def upload_mtf_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        result = await WebMTFService.upload(user_id=current_user.id, file=file)
        with WebMTFService._lock:
            dataframe = WebMTFService._datasets[current_user.id].copy()

        PersistentUploadService.save_dataframe(
            db,
            user_id=current_user.id,
            dataset_type=PersistentUploadService.MTF,
            filename=file.filename or "mtf-upload",
            content_type=file.content_type,
            dataframe=dataframe,
        )
        return result
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error)) from error


@router.get("/dashboard", response_model=MTFDashboardResponse)
def get_mtf_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    if not _restore(db, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No saved MTF upload was found.")
    return WebMTFService.dashboard(user_id=current_user.id)


@router.get("/client-risk", response_model=list[ClientRiskItem])
def get_client_risk(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    if not _restore(db, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No saved MTF upload was found.")
    return WebMTFService.client_risk(user_id=current_user.id)


@router.get("/symbol-exposure", response_model=list[SymbolExposureItem])
def get_symbol_exposure(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict]:
    if not _restore(db, current_user.id):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No saved MTF upload was found.")
    return WebMTFService.symbol_exposure(user_id=current_user.id)


@router.get("/uploads", response_model=list[UploadHistoryItem])
def mtf_upload_history(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return PersistentUploadService.list_history(
        db,
        user_id=current_user.id,
        dataset_type=PersistentUploadService.MTF,
    )


@router.post("/uploads/{upload_id}/activate", response_model=MTFDashboardResponse)
def activate_mtf_upload(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        PersistentUploadService.activate(
            db,
            user_id=current_user.id,
            dataset_type=PersistentUploadService.MTF,
            upload_id=upload_id,
        )
        PersistentUploadService.clear_cache(
            user_id=current_user.id,
            cache=WebMTFService._datasets,
            lock=WebMTFService._lock,
        )
        _restore(db, current_user.id)
        return WebMTFService.dashboard(user_id=current_user.id)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error


@router.delete("/uploads/{upload_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_mtf_upload(
    upload_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Response:
    try:
        PersistentUploadService.delete(
            db,
            user_id=current_user.id,
            dataset_type=PersistentUploadService.MTF,
            upload_id=upload_id,
        )
        PersistentUploadService.clear_cache(
            user_id=current_user.id,
            cache=WebMTFService._datasets,
            lock=WebMTFService._lock,
        )
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ValueError as error:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(error)) from error
