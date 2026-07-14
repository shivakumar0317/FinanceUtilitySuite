"""
Finance Utility Suite
Portfolio Performance Service

Generates portfolio performance history automatically from Yahoo Finance
using current holdings and historical close prices.

Version: 1.30 Beta
"""

from __future__ import annotations

from datetime import datetime, timedelta

import pandas as pd
import yfinance as yf


class PortfolioPerformanceService:
    """Service for generating portfolio performance history."""

    DEFAULT_PERIOD_DAYS = 365

    SYMBOL_COLUMNS = ("SYMBOL", "Symbol", "symbol")
    QTY_COLUMNS = ("QTY", "Qty", "Quantity", "quantity", "NetQty", "NETQTY")

    @classmethod
    def generate_history(
        cls,
        dataframe: pd.DataFrame,
        days: int = DEFAULT_PERIOD_DAYS,
    ) -> tuple[pd.DataFrame, dict]:
        """Generate portfolio value history and performance summary."""

        if dataframe is None or dataframe.empty:
            raise ValueError("Portfolio data is empty.")

        symbol_col = cls._find_column(dataframe, cls.SYMBOL_COLUMNS)
        qty_col = cls._find_column(dataframe, cls.QTY_COLUMNS)

        if symbol_col is None:
            raise ValueError("Symbol column not found. Required: SYMBOL or Symbol.")

        if qty_col is None:
            raise ValueError("Quantity column not found. Required: QTY, Quantity or NetQty.")

        holdings = dataframe[[symbol_col, qty_col]].copy()
        holdings.columns = ["SYMBOL", "QTY"]
        holdings["SYMBOL"] = holdings["SYMBOL"].astype(str).str.strip().str.upper()
        holdings["QTY"] = pd.to_numeric(holdings["QTY"], errors="coerce").fillna(0)
        holdings = holdings[(holdings["SYMBOL"] != "") & (holdings["QTY"] != 0)]

        if holdings.empty:
            raise ValueError("No valid holdings found for performance calculation.")

        start_date = datetime.today() - timedelta(days=days)
        end_date = datetime.today() + timedelta(days=1)

        portfolio_history: pd.DataFrame | None = None

        for _, row in holdings.iterrows():
            symbol = row["SYMBOL"]
            quantity = float(row["QTY"])

            price_data = cls._download_price_history(
                symbol=symbol,
                start_date=start_date,
                end_date=end_date,
            )

            if price_data.empty:
                continue

            stock_value = price_data[["Close"]].copy()
            stock_value.rename(columns={"Close": symbol}, inplace=True)
            stock_value[symbol] = stock_value[symbol] * quantity

            if portfolio_history is None:
                portfolio_history = stock_value
            else:
                portfolio_history = portfolio_history.join(stock_value, how="outer")

        if portfolio_history is None or portfolio_history.empty:
            raise ValueError("Unable to download historical price data from Yahoo Finance.")

        portfolio_history = portfolio_history.sort_index().ffill().dropna(how="all")
        portfolio_history["Portfolio Value"] = portfolio_history.sum(axis=1)

        result = pd.DataFrame()
        result["Date"] = portfolio_history.index
        result["Portfolio Value"] = portfolio_history["Portfolio Value"].values
        result["Daily P/L"] = result["Portfolio Value"].diff().fillna(0)
        result["Daily Return %"] = result["Portfolio Value"].pct_change().fillna(0) * 100
        result["Cumulative Return %"] = (
            result["Portfolio Value"] / result["Portfolio Value"].iloc[0] - 1
        ) * 100

        result["Peak Value"] = result["Portfolio Value"].cummax()
        result["Drawdown %"] = (
            result["Portfolio Value"] / result["Peak Value"] - 1
        ) * 100

        summary = cls._summary(result)

        return result, summary

    @classmethod
    def _download_price_history(
        cls,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
    ) -> pd.DataFrame:
        """Download historical close price with NSE/BSE fallback."""

        tickers = [f"{symbol}.NS", f"{symbol}.BO", symbol]

        for ticker_symbol in tickers:
            try:
                data = yf.download(
                    ticker_symbol,
                    start=start_date.strftime("%Y-%m-%d"),
                    end=end_date.strftime("%Y-%m-%d"),
                    progress=False,
                    auto_adjust=False,
                    threads=False,
                )

                if data is not None and not data.empty and "Close" in data.columns:
                    close_data = data[["Close"]].dropna()
                    if not close_data.empty:
                        return close_data

            except Exception:
                continue

        return pd.DataFrame()

    @staticmethod
    def _summary(dataframe: pd.DataFrame) -> dict:
        """Calculate performance summary metrics."""

        start_value = float(dataframe["Portfolio Value"].iloc[0])
        end_value = float(dataframe["Portfolio Value"].iloc[-1])
        total_return = ((end_value / start_value) - 1) * 100 if start_value else 0
        max_drawdown = float(dataframe["Drawdown %"].min())

        days = max((dataframe["Date"].iloc[-1] - dataframe["Date"].iloc[0]).days, 1)
        cagr = ((end_value / start_value) ** (365 / days) - 1) * 100 if start_value else 0

        best_day = float(dataframe["Daily P/L"].max())
        worst_day = float(dataframe["Daily P/L"].min())

        return {
            "start_value": start_value,
            "end_value": end_value,
            "total_return": total_return,
            "cagr": cagr,
            "max_drawdown": max_drawdown,
            "best_day": best_day,
            "worst_day": worst_day,
            "days": days,
        }

    @staticmethod
    def _find_column(dataframe: pd.DataFrame, possible_columns: tuple[str, ...]) -> str | None:
        """Find first matching column from possible column names."""

        for column in possible_columns:
            if column in dataframe.columns:
                return column

        return None
