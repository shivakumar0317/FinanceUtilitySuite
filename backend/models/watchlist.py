from __future__ import annotations
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.database import Base
if TYPE_CHECKING:
    from backend.models.user import User
class WatchlistItem(Base):
    __tablename__ = "watchlist_items"
    __table_args__ = (UniqueConstraint("user_id","symbol",name="uq_watchlist_user_symbol"),)
    id: Mapped[int] = mapped_column(primary_key=True,index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id",ondelete="CASCADE"),nullable=False,index=True)
    symbol: Mapped[str] = mapped_column(String(40),nullable=False,index=True)
    exchange: Mapped[str] = mapped_column(String(20),nullable=False,default="NSE")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now())
    user: Mapped["User"] = relationship(back_populates="watchlist_items")
