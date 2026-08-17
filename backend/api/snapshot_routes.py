"""
Enterprise RMS Snapshot API

Provides snapshot history and snapshot comparison
for the Enterprise RMS web application.

Author : Shiva Kumar
Version : 1.0.0
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.snapshot_schema import (
    SnapshotComparisonSchema,
    SnapshotHistoryItem,
)
from core.services.snapshot_service import SnapshotService


router = APIRouter(
    prefix="/snapshots",
    tags=["Enterprise RMS Snapshots"],
)


service = SnapshotService()


# ---------------------------------------------------------
# Snapshot History
# ---------------------------------------------------------


@router.get(
    "",
    response_model=list[SnapshotHistoryItem],
)
def list_snapshots(
    current_user: User = Depends(get_current_user),
) -> list[SnapshotHistoryItem]:
    """
    Return all available Enterprise RMS snapshots.
    """

    snapshots = service.list_snapshots()

    return [
        SnapshotHistoryItem(
            snapshot_id=item.snapshot_id,
            business_date=item.business_date,
            timestamp=item.timestamp,
            filename=item.filename,
            records=item.records,
            clients=item.clients,
            symbols=item.symbols,
            portfolio_value=item.portfolio_value,
            total_exposure=item.total_exposure,
            total_mtm=item.total_mtm,
            risk_score=item.risk_score,
            health=item.health,
            margin_utilization=item.margin_utilization,
            diversification_score=item.diversification_score,
            top_client_concentration=item.top_client_concentration,
            top_symbol_concentration=item.top_symbol_concentration,
            source_file=item.source_file,
            notes=item.notes,
        )
        for item in snapshots
    ]


# ---------------------------------------------------------
# Latest Snapshot
# ---------------------------------------------------------


@router.get(
    "/latest",
    response_model=SnapshotHistoryItem,
)
def latest_snapshot(
    current_user: User = Depends(get_current_user),
) -> SnapshotHistoryItem:
    """
    Return the latest Enterprise RMS snapshot.
    """

    snapshot = service.latest_snapshot()

    if snapshot is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No snapshot is available.",
        )

    return SnapshotHistoryItem(
        snapshot_id=snapshot.snapshot_id,
        business_date=snapshot.business_date,
        timestamp=snapshot.timestamp,
        filename=snapshot.filename,
        records=snapshot.records,
        clients=snapshot.clients,
        symbols=snapshot.symbols,
        portfolio_value=snapshot.portfolio_value,
        total_exposure=snapshot.total_exposure,
        total_mtm=snapshot.total_mtm,
        risk_score=snapshot.risk_score,
        health=snapshot.health,
        margin_utilization=snapshot.margin_utilization,
        diversification_score=snapshot.diversification_score,
        top_client_concentration=snapshot.top_client_concentration,
        top_symbol_concentration=snapshot.top_symbol_concentration,
        source_file=snapshot.source_file,
        notes=snapshot.notes,
    )


# ---------------------------------------------------------
# Snapshot Comparison
# ---------------------------------------------------------


@router.get(
    "/compare/{first_snapshot_id}/{second_snapshot_id}",
    response_model=SnapshotComparisonSchema,
)
def compare_snapshots(
    first_snapshot_id: str,
    second_snapshot_id: str,
    current_user: User = Depends(get_current_user),
) -> SnapshotComparisonSchema:
    """
    Compare two Enterprise RMS snapshots.
    """

    try:
        result = service.compare_snapshots(
            first_snapshot_id,
            second_snapshot_id,
        )
    except FileNotFoundError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Snapshot not found: {error}",
        ) from error

    return SnapshotComparisonSchema(**result)