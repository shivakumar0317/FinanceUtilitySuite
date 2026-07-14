from fastapi import APIRouter, HTTPException, Query
from backend.services.market_service import MarketService

router=APIRouter(prefix='/api/market',tags=['Market'])

@router.get('/quote/{symbol}')
def quote(symbol:str):
    try:return MarketService.quote(symbol)
    except ValueError as e:raise HTTPException(404,str(e)) from e

@router.get('/history/{symbol}')
def history(symbol:str,period:str=Query('1mo'),interval:str=Query('1d')):
    try:return MarketService.history(symbol,period,interval)
    except ValueError as e:raise HTTPException(404,str(e)) from e
