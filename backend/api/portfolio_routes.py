from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from backend.auth.dependencies import get_current_user
from backend.database import get_db
from backend.models.holding import Holding
from backend.models.portfolio import Portfolio
from backend.models.user import User
from backend.schemas.holding_schema import HoldingCreate, HoldingRead, HoldingUpdate
from backend.schemas.portfolio_schema import (
    PortfolioCreate,
    PortfolioDetail,
    PortfolioRead,
    PortfolioUpdate,
)

router = APIRouter(prefix="/api", tags=["Portfolio"])


def get_owned_portfolio(
    portfolio_id: int,
    current_user: User,
    db: Session,
    include_holdings: bool = False,
) -> Portfolio:
    statement = select(Portfolio).where(
        Portfolio.id == portfolio_id,
        Portfolio.user_id == current_user.id,
    )
    if include_holdings:
        statement = statement.options(selectinload(Portfolio.holdings))

    portfolio = db.scalar(statement)
    if portfolio is None:
        raise HTTPException(status_code=404, detail="Portfolio not found.")
    return portfolio


def get_owned_holding(
    holding_id: int,
    current_user: User,
    db: Session,
) -> Holding:
    statement = (
        select(Holding)
        .join(Portfolio, Holding.portfolio_id == Portfolio.id)
        .where(
            Holding.id == holding_id,
            Portfolio.user_id == current_user.id,
        )
    )
    holding = db.scalar(statement)
    if holding is None:
        raise HTTPException(status_code=404, detail="Holding not found.")
    return holding


@router.post("/portfolios", response_model=PortfolioRead, status_code=201)
def create_portfolio(
    payload: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    portfolio = Portfolio(
        name=payload.name,
        description=payload.description,
        user_id=current_user.id,
    )
    db.add(portfolio)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="You already have a portfolio with this name.",
        ) from error
    db.refresh(portfolio)
    return portfolio


@router.get("/portfolios", response_model=list[PortfolioRead])
def list_portfolios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    statement = (
        select(Portfolio)
        .where(Portfolio.user_id == current_user.id)
        .order_by(Portfolio.created_at.desc())
    )
    return list(db.scalars(statement).all())


@router.get("/portfolios/{portfolio_id}", response_model=PortfolioDetail)
def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_owned_portfolio(
        portfolio_id,
        current_user,
        db,
        include_holdings=True,
    )


@router.patch("/portfolios/{portfolio_id}", response_model=PortfolioRead)
def update_portfolio(
    portfolio_id: int,
    payload: PortfolioUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    portfolio = get_owned_portfolio(portfolio_id, current_user, db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(portfolio, key, value)

    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="You already have a portfolio with this name.",
        ) from error

    db.refresh(portfolio)
    return portfolio


@router.delete("/portfolios/{portfolio_id}", status_code=204)
def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    portfolio = get_owned_portfolio(portfolio_id, current_user, db)
    db.delete(portfolio)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post("/holdings", response_model=HoldingRead, status_code=201)
def create_holding(
    payload: HoldingCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_portfolio(payload.portfolio_id, current_user, db)

    holding = Holding(**payload.model_dump())
    db.add(holding)
    try:
        db.commit()
    except IntegrityError as error:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="This symbol already exists in the portfolio.",
        ) from error

    db.refresh(holding)
    return holding


@router.get(
    "/portfolios/{portfolio_id}/holdings",
    response_model=list[HoldingRead],
)
def list_holdings(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    get_owned_portfolio(portfolio_id, current_user, db)
    statement = (
        select(Holding)
        .where(Holding.portfolio_id == portfolio_id)
        .order_by(Holding.symbol)
    )
    return list(db.scalars(statement).all())


@router.patch("/holdings/{holding_id}", response_model=HoldingRead)
def update_holding(
    holding_id: int,
    payload: HoldingUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    holding = get_owned_holding(holding_id, current_user, db)
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(holding, key, value)

    db.commit()
    db.refresh(holding)
    return holding


@router.delete("/holdings/{holding_id}", status_code=204)
def delete_holding(
    holding_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    holding = get_owned_holding(holding_id, current_user, db)
    db.delete(holding)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
