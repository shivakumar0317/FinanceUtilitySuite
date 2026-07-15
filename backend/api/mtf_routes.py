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
from backend.schemas.mtf_schema import (
    ClientRiskItem,
    MTFDashboardResponse,
    SymbolExposureItem,
)
from backend.services.web_mtf_service import WebMTFService


router = APIRouter(
    prefix="/api/mtf",
    tags=["MTF Dashboard"],
)


@router.post(
    "/upload",
    response_model=MTFDashboardResponse,
)
async def upload_mtf_file(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        return await WebMTFService.upload(
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
    response_model=MTFDashboardResponse,
)
def get_mtf_dashboard(
    current_user: User = Depends(get_current_user),
) -> dict:
    try:
        return WebMTFService.dashboard(
            user_id=current_user.id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/client-risk",
    response_model=list[ClientRiskItem],
)
def get_client_risk(
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    try:
        return WebMTFService.client_risk(
            user_id=current_user.id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get(
    "/symbol-exposure",
    response_model=list[SymbolExposureItem],
)
def get_symbol_exposure(
    current_user: User = Depends(get_current_user),
) -> list[dict]:
    try:
        return WebMTFService.symbol_exposure(
            user_id=current_user.id,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error
