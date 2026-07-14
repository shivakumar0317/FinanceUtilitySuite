from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf
from sqlalchemy import select
from sqlalchemy.orm import Session

from backend.models.holding import Holding
from backend.models.portfolio import Portfolio
from backend.models.user import User


class AnalyticsService:
    HISTORY_DAYS = 180

    @classmethod
    def dashboard(cls, db: Session, current_user: User) -> dict:
        holdings = cls._load_holdings(db, current_user)
        if not holdings:
            return {
                'summary': {
                    'total_investment': 0.0,
                    'current_value': 0.0,
                    'profit_loss': 0.0,
                    'profit_loss_percent': 0.0,
                    'total_holdings': 0,
                },
                'allocation': [],
                'profit_loss': [],
                'top_holdings': [],
                'performance': [],
            }

        rows = []
        for holding in holdings:
            quote = cls._quote(holding.symbol, holding.exchange)
            quantity = float(holding.quantity)
            average_price = float(holding.average_price)
            investment_value = quantity * average_price
            current_value = quantity * quote['price']
            profit_loss = current_value - investment_value
            profit_loss_percent = (profit_loss / investment_value * 100) if investment_value else 0.0
            rows.append({
                'symbol': holding.symbol,
                'quantity': quantity,
                'investment_value': investment_value,
                'current_value': current_value,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent,
                'sector': quote['sector'],
                'resolved_symbol': quote['resolved_symbol'],
            })

        total_investment = sum(r['investment_value'] for r in rows)
        current_value = sum(r['current_value'] for r in rows)
        profit_loss = current_value - total_investment
        profit_loss_percent = (profit_loss / total_investment * 100) if total_investment else 0.0

        sector_totals = {}
        for row in rows:
            sector_totals[row['sector']] = sector_totals.get(row['sector'], 0.0) + row['current_value']

        return {
            'summary': {
                'total_investment': round(total_investment, 2),
                'current_value': round(current_value, 2),
                'profit_loss': round(profit_loss, 2),
                'profit_loss_percent': round(profit_loss_percent, 2),
                'total_holdings': len(rows),
            },
            'allocation': [
                {'name': k, 'value': round(v, 2)}
                for k, v in sorted(sector_totals.items(), key=lambda x: x[1], reverse=True)
            ],
            'profit_loss': [
                {
                    'symbol': r['symbol'],
                    'profit_loss': round(r['profit_loss'], 2),
                    'profit_loss_percent': round(r['profit_loss_percent'], 2),
                }
                for r in sorted(rows, key=lambda x: x['profit_loss'], reverse=True)
            ],
            'top_holdings': [
                {'symbol': r['symbol'], 'value': round(r['current_value'], 2)}
                for r in sorted(rows, key=lambda x: x['current_value'], reverse=True)[:10]
            ],
            'performance': cls._performance(rows),
        }

    @staticmethod
    def _load_holdings(db: Session, current_user: User) -> list[Holding]:
        statement = (
            select(Holding)
            .join(Portfolio, Holding.portfolio_id == Portfolio.id)
            .where(Portfolio.user_id == current_user.id)
            .order_by(Holding.symbol)
        )
        return list(db.scalars(statement).all())

    @classmethod
    def _quote(cls, symbol: str, exchange: str) -> dict:
        for candidate in cls._ticker_candidates(symbol, exchange):
            try:
                ticker = yf.Ticker(candidate)
                history = ticker.history(period='5d', auto_adjust=False)
                if history is None or history.empty:
                    continue
                close = history['Close'].dropna()
                if close.empty:
                    continue
                sector = 'Other'
                try:
                    info = ticker.get_info()
                    sector = info.get('sector') or info.get('industry') or 'Other'
                except Exception:
                    pass
                return {
                    'price': float(close.iloc[-1]),
                    'sector': sector,
                    'resolved_symbol': candidate,
                }
            except Exception:
                continue
        return {'price': 0.0, 'sector': 'Other', 'resolved_symbol': symbol}

    @classmethod
    def _performance(cls, rows: list[dict]) -> list[dict]:
        end_date = datetime.today()
        start_date = end_date - timedelta(days=cls.HISTORY_DAYS)
        portfolio_series = None
        for row in rows:
            try:
                data = yf.download(
                    row['resolved_symbol'],
                    start=start_date.strftime('%Y-%m-%d'),
                    end=(end_date + timedelta(days=1)).strftime('%Y-%m-%d'),
                    auto_adjust=True,
                    progress=False,
                    threads=False,
                )
                if data is None or data.empty:
                    continue
                close = data['Close']
                if isinstance(close, pd.DataFrame):
                    close = close.iloc[:, 0]
                close = pd.to_numeric(close, errors='coerce').dropna()
                values = close * row['quantity']
                portfolio_series = values if portfolio_series is None else portfolio_series.add(values, fill_value=0)
            except Exception:
                continue
        if portfolio_series is None or portfolio_series.empty:
            return []
        portfolio_series = portfolio_series.sort_index().ffill().dropna()
        return [
            {'date': pd.Timestamp(i).strftime('%Y-%m-%d'), 'value': round(float(v), 2)}
            for i, v in portfolio_series.items()
        ]

    @staticmethod
    def _ticker_candidates(symbol: str, exchange: str) -> list[str]:
        cleaned = symbol.strip().upper()
        if cleaned.endswith(('.NS', '.BO')):
            return [cleaned]
        if (exchange or 'NSE').strip().upper() == 'BSE':
            return [f'{cleaned}.BO', f'{cleaned}.NS', cleaned]
        return [f'{cleaned}.NS', f'{cleaned}.BO', cleaned]
