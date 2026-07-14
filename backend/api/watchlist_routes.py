from fastapi import APIRouter,Depends,HTTPException,Response,status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models.user import User
from backend.models.watchlist import WatchlistItem
from backend.schemas.watchlist_schema import WatchlistCreate
from backend.services.market_dashboard_service import MarketDashboardService
router=APIRouter(prefix="/api/watchlist",tags=["Watchlist"])
@router.get("")
def list_items(current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    items=list(db.scalars(select(WatchlistItem).where(WatchlistItem.user_id==current_user.id).order_by(WatchlistItem.created_at.desc())).all())
    return [{"id":i.id,"symbol":i.symbol,"exchange":i.exchange,"created_at":i.created_at,**MarketDashboardService.quote(i.symbol,i.exchange)} for i in items]
@router.post("",status_code=201)
def add_item(payload:WatchlistCreate,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=WatchlistItem(user_id=current_user.id,symbol=payload.symbol,exchange=payload.exchange); db.add(item)
    try: db.commit()
    except IntegrityError as e:
        db.rollback(); raise HTTPException(409,"This symbol is already in your watchlist.") from e
    db.refresh(item)
    return {"id":item.id,"symbol":item.symbol,"exchange":item.exchange,"created_at":item.created_at,**MarketDashboardService.quote(item.symbol,item.exchange)}
@router.delete("/{symbol}",status_code=204)
def delete_item(symbol:str,current_user:User=Depends(get_current_user),db:Session=Depends(get_db)):
    item=db.scalar(select(WatchlistItem).where(WatchlistItem.user_id==current_user.id,WatchlistItem.symbol==symbol.strip().upper()))
    if item is None: raise HTTPException(404,"Watchlist item not found.")
    db.delete(item); db.commit(); return Response(status_code=status.HTTP_204_NO_CONTENT)
