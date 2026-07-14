from fastapi import APIRouter,Depends,Query
from backend.auth.dependencies import get_current_user
from backend.models.user import User
from backend.services.market_dashboard_service import MarketDashboardService
router=APIRouter(prefix="/api/market-dashboard",tags=["Market Dashboard"])
@router.get("/indices")
def indices(_user:User=Depends(get_current_user)):
    return MarketDashboardService.indices()
@router.get("/top-movers")
def movers(limit:int=Query(5,ge=1,le=20),_user:User=Depends(get_current_user)):
    return MarketDashboardService.top_movers(limit)
