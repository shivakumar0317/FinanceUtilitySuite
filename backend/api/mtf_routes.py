from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy.orm import Session

from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.schemas.mtf_schema import (ClientRiskItem, MTFDashboardResponse, MTFUploadResponse, SymbolExposureItem)
from backend.schemas.upload_dataset_schema import UploadHistoryItem
from backend.services.persistent_upload_service import PersistentUploadService
from backend.services.web_mtf_service import WebMTFService

from core.services.master_import_service import MasterImportService
from core.services.snapshot_service import SnapshotService

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


@router.post("/upload", response_model=MTFUploadResponse)
async def upload_mtf_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    try:
        # -------------------------------------------------
        # 1. Prepare the uploaded MTF dataframe
        #
        # WebMTFService returns the Web-compatible dataframe
        # used by the existing Web MTF Dashboard.
        # -------------------------------------------------
        web_dataframe = await WebMTFService.prepare_upload(file)

        # -------------------------------------------------
        # 2. Store Web-compatible dataset
        #
        # Keep this representation because the existing
        # Web MTF Dashboard expects ACCOUNTID / SYMBOL /
        # NETVALUE / NETQTY / MARKTOMARKET.
        # -------------------------------------------------
        with WebMTFService._lock:
            WebMTFService._datasets[current_user.id] = (
                web_dataframe
            )

        # -------------------------------------------------
        # 3. Persist Web-compatible dataset
        #
        # This keeps the existing restore/dashboard flow
        # compatible.
        # -------------------------------------------------
        PersistentUploadService.save_dataframe(
            db,
            user_id=current_user.id,
            dataset_type=PersistentUploadService.MTF,
            filename=file.filename or "mtf-upload",
            content_type=file.content_type,
            dataframe=web_dataframe,
        )

        # -------------------------------------------------
        # 4. Convert Web dataframe BACK to canonical MTF
        #    column names for Enterprise RMS.
        #
        # MTFImportService is the canonical MTF pipeline.
        # MasterImportService validates BEFORE normalization,
        # therefore it must receive canonical column names.
        # -------------------------------------------------
        canonical_dataframe = web_dataframe.rename(
            columns={
                "ACCOUNTID": "AccountId",
                "SYMBOL": "Symbol",
                "NETVALUE": "NetValue",
                "NETQTY": "NetQty",
                "MARKTOMARKET": "MarkToMarket",
            }
        )

        # -------------------------------------------------
        # 5. Create Enterprise RMS snapshot
        # -------------------------------------------------
        import_result = MasterImportService.import_dataframe(
            canonical_dataframe,
            source_name=file.filename or "mtf-upload",
        )

        # -------------------------------------------------
        # 6. Retrieve the newly created snapshot metadata
        # -------------------------------------------------
        snapshot_service = SnapshotService()

        snapshot = snapshot_service.repository.get_metadata(
            import_result.snapshot_id
        )

        if snapshot is None:
            raise ValueError(
                "MTF upload succeeded, but the Enterprise RMS "
                "snapshot could not be retrieved."
            )

        # -------------------------------------------------
        # 7. Build existing Web MTF dashboard
        # -------------------------------------------------
        dashboard = WebMTFService.dashboard(
            user_id=current_user.id,
        )

        # -------------------------------------------------
        # 8. Return dashboard + snapshot information
        # -------------------------------------------------
        return {
            "dashboard": dashboard,
            "snapshot": {
                "snapshot_id": snapshot.snapshot_id,
                "business_date": snapshot.business_date,
                "filename": snapshot.filename,
                "records": snapshot.records,
                "clients": snapshot.clients,
                "symbols": snapshot.symbols,
                "total_exposure": snapshot.total_exposure,
                "total_mtm": snapshot.total_mtm,
                "risk_score": snapshot.risk_score,
                "health": snapshot.health,
            },
        }

    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(error),
        ) from error


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
