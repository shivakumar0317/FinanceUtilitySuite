from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.services.persistent_upload_service import (
    PersistentUploadService,
)
from backend.services.web_mtf_concentration_service import (
    WebMTFConcentrationService,
)

# Use the same authentication dependency used by the existing MTF routes.
from backend.auth.dependencies import get_current_user


router = APIRouter(
    prefix="/api/mtf",
    tags=["MTF Concentration"],
)


def _records_to_dicts(dataframe):
    if dataframe is None or dataframe.empty:
        return []

    return dataframe.to_dict(orient="records")


@router.get("/concentration")
def get_mtf_concentration(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    user_id = current_user.id

    dataframe = (
        PersistentUploadService.restore_dataframe(
            db,
            user_id=user_id,
            dataset_type=PersistentUploadService.MTF,
        )
    )

    if dataframe is None or dataframe.empty:
        raise HTTPException(
            status_code=404,
            detail="Upload an MTF Excel or CSV file first.",
        )

    try:
        summary = WebMTFConcentrationService.calculate(
            dataframe
        )

        dashboard_summary = (
            WebMTFConcentrationService.get_summary(
                summary
            )
        )

        return {
            "summary": dashboard_summary,
            "distribution": (
                WebMTFConcentrationService.distribution(
                    summary
                )
            ),
            "risk_distribution": (
                WebMTFConcentrationService.risk_distribution(
                    summary
                )
            ),
            "single_stock_clients": _records_to_dicts(
                WebMTFConcentrationService.single_stock_clients(
                    summary
                )
            ),
            "top_concentrated_clients": _records_to_dicts(
                WebMTFConcentrationService.top_concentrated_clients(
                    summary
                )
            ),
            "multiple_stock_clients": _records_to_dicts(
                WebMTFConcentrationService.multiple_stock_clients(
                    summary
                )
            ),
            "client_summary": _records_to_dicts(
                summary
            ),
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc
