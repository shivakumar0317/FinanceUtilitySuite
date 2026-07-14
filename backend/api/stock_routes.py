from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse

from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.schemas.stock_schema import StockAnalyzerResponse
from backend.services.stock_analyzer_service import StockAnalyzerService


router = APIRouter(prefix="/api/stocks", tags=["Stock Analyzer"])


@router.get("/{symbol}", response_model=StockAnalyzerResponse)
def analyze_stock(
    symbol: str,
    period: str = Query(default="1y"),
    interval: str = Query(default="1d"),
    _current_user: User = Depends(get_current_user),
) -> dict:
    try:
        return StockAnalyzerService.analyze(symbol, period, interval)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error


@router.get("/{symbol}/export")
def export_stock_analysis(
    symbol: str,
    period: str = Query(default="1y"),
    _current_user: User = Depends(get_current_user),
) -> StreamingResponse:
    try:
        output = StockAnalyzerService.export_excel(symbol, period)
    except ValueError as error:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(error),
        ) from error

    filename = f"{symbol.strip().upper()}_Stock_Analysis.xlsx"

    return StreamingResponse(
        output,
        media_type=(
            "application/vnd.openxmlformats-officedocument."
            "spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"',
        },
    )
