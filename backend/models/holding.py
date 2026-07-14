from __future__ import annotations

from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, Numeric, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base

if TYPE_CHECKING:
    from backend.models.portfolio import Portfolio


class Holding(Base):
    __tablename__ = "holdings"
    __table_args__ = (
        UniqueConstraint(
            "portfolio_id",
            "symbol",
            name="uq_holding_portfolio_symbol",
        ),
    )

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    portfolio_id: Mapped[int] = mapped_column(
        ForeignKey("portfolios.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    symbol: Mapped[str] = mapped_column(String(40), nullable=False, index=True)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    average_price: Mapped[Decimal] = mapped_column(Numeric(18, 4), nullable=False)
    exchange: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="NSE",
    )

    portfolio: Mapped["Portfolio"] = relationship(back_populates="holdings")
