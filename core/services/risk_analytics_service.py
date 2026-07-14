"""
Finance Utility Suite
Risk Analytics Service

Version: 1.30
Generates portfolio risk analytics using Yahoo Finance history.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd
import yfinance as yf


@dataclass
class RiskAnalyticsResult:
    history: pd.DataFrame
    metrics: dict


class RiskAnalyticsService:
    """Calculate portfolio risk metrics versus Nifty 50."""

    BENCHMARK_SYMBOL = "^NSEI"
    TRADING_DAYS = 252
    RISK_FREE_RATE = 0.06

    SYMBOL_COLUMNS = ("SYMBOL", "Symbol", "symbol")
    QTY_COLUMNS = ("QTY", "Qty", "Quantity", "quantity", "NetQty")
    VALUE_COLUMNS = ("CURRENT_VALUE", "Current Value", "Investment Value", "VALUE")

    @classmethod
    def analyze(
        cls,
        dataframe: pd.DataFrame,
        period: str = "1y",
        benchmark_symbol: str = BENCHMARK_SYMBOL,
    ) -> RiskAnalyticsResult:
        """Generate portfolio history, benchmark history and risk metrics."""

        if dataframe is None or dataframe.empty:
            raise ValueError("Portfolio data is empty.")

        holdings = cls._normalize_holdings(dataframe)
        portfolio_history = cls._build_portfolio_history(holdings, period)
        benchmark_history = cls._download_price_series(benchmark_symbol, period)

        history = pd.concat(
            [
                portfolio_history.rename("Portfolio"),
                benchmark_history.rename("Benchmark"),
            ],
            axis=1,
        ).dropna()

        if history.empty or len(history) < 5:
            raise ValueError("Not enough historical data to calculate risk analytics.")

        history["Portfolio Return"] = history["Portfolio"].pct_change()
        history["Benchmark Return"] = history["Benchmark"].pct_change()
        history = history.dropna()

        history["Portfolio Growth"] = (
            100 * (1 + history["Portfolio Return"]).cumprod()
        )
        history["Benchmark Growth"] = (
            100 * (1 + history["Benchmark Return"]).cumprod()
        )

        history["Portfolio Peak"] = history["Portfolio Growth"].cummax()
        history["Drawdown %"] = (
            (history["Portfolio Growth"] - history["Portfolio Peak"])
            / history["Portfolio Peak"]
            * 100
        )

        metrics = cls._calculate_metrics(history)

        return RiskAnalyticsResult(history=history.reset_index(), metrics=metrics)

    @classmethod
    def _normalize_holdings(cls, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Normalize symbol, quantity and weight/value columns."""

        symbol_col = cls._find_column(dataframe, cls.SYMBOL_COLUMNS)
        qty_col = cls._find_column(dataframe, cls.QTY_COLUMNS)
        value_col = cls._find_column(dataframe, cls.VALUE_COLUMNS, required=False)

        if symbol_col is None:
            raise ValueError("Portfolio must contain SYMBOL or Symbol column.")

        holdings = dataframe.copy()
        holdings["SYMBOL_CLEAN"] = holdings[symbol_col].astype(str).str.upper().str.strip()

        if qty_col is not None:
            holdings["QTY_CLEAN"] = pd.to_numeric(holdings[qty_col], errors="coerce").fillna(0)
        else:
            holdings["QTY_CLEAN"] = 1

        if value_col is not None:
            holdings["VALUE_CLEAN"] = pd.to_numeric(
                holdings[value_col], errors="coerce"
            ).fillna(0)
        else:
            holdings["VALUE_CLEAN"] = holdings["QTY_CLEAN"]

        holdings = holdings[
            (holdings["SYMBOL_CLEAN"] != "")
            & (holdings["QTY_CLEAN"] > 0)
        ].copy()

        if holdings.empty:
            raise ValueError("No valid holdings found for risk analytics.")

        return holdings[["SYMBOL_CLEAN", "QTY_CLEAN", "VALUE_CLEAN"]]

    @classmethod
    def _build_portfolio_history(
        cls,
        holdings: pd.DataFrame,
        period: str,
    ) -> pd.Series:
        """Build portfolio value history from Yahoo Finance price history."""

        series_list = []

        for _, row in holdings.iterrows():
            symbol = row["SYMBOL_CLEAN"]
            quantity = float(row["QTY_CLEAN"])

            price_series = cls._download_price_series(cls._to_nse_symbol(symbol), period)

            if price_series.empty:
                price_series = cls._download_price_series(symbol, period)

            if price_series.empty:
                continue

            series_list.append(price_series * quantity)

        if not series_list:
            raise ValueError("Unable to download historical prices for portfolio holdings.")

        portfolio_history = pd.concat(series_list, axis=1).dropna(how="all")
        portfolio_history = portfolio_history.ffill().dropna(how="all")

        return portfolio_history.sum(axis=1)

    @staticmethod
    def _download_price_series(symbol: str, period: str) -> pd.Series:
        """Download adjusted close or close price series."""

        try:
            data = yf.download(
                symbol,
                period=period,
                auto_adjust=True,
                progress=False,
                threads=False,
            )

            if data is None or data.empty:
                return pd.Series(dtype=float)

            if "Close" in data.columns:
                series = data["Close"]
            elif "Adj Close" in data.columns:
                series = data["Adj Close"]
            else:
                return pd.Series(dtype=float)

            if isinstance(series, pd.DataFrame):
                series = series.iloc[:, 0]

            series = pd.to_numeric(series, errors="coerce").dropna()
            series.name = symbol
            return series

        except Exception:
            return pd.Series(dtype=float)

    @classmethod
    def _calculate_metrics(cls, history: pd.DataFrame) -> dict:
        """Calculate beta, alpha, Sharpe, volatility and drawdown."""

        portfolio_returns = history["Portfolio Return"]
        benchmark_returns = history["Benchmark Return"]

        portfolio_total_return = (
            history["Portfolio Growth"].iloc[-1] / history["Portfolio Growth"].iloc[0] - 1
        )
        benchmark_total_return = (
            history["Benchmark Growth"].iloc[-1] / history["Benchmark Growth"].iloc[0] - 1
        )

        volatility = portfolio_returns.std() * math.sqrt(cls.TRADING_DAYS)

        benchmark_variance = benchmark_returns.var()
        beta = (
            portfolio_returns.cov(benchmark_returns) / benchmark_variance
            if benchmark_variance
            else 0
        )

        expected_return = cls.RISK_FREE_RATE + beta * (
            benchmark_total_return - cls.RISK_FREE_RATE
        )
        alpha = portfolio_total_return - expected_return

        sharpe = (
            (portfolio_returns.mean() * cls.TRADING_DAYS - cls.RISK_FREE_RATE)
            / volatility
            if volatility
            else 0
        )

        max_drawdown = history["Drawdown %"].min()

        return {
            "Portfolio Return": portfolio_total_return * 100,
            "Benchmark Return": benchmark_total_return * 100,
            "Beta": beta,
            "Alpha": alpha * 100,
            "Sharpe Ratio": sharpe,
            "Volatility": volatility * 100,
            "Max Drawdown": max_drawdown,
        }

    @staticmethod
    def _to_nse_symbol(symbol: str) -> str:
        """Convert plain Indian stock symbol to NSE Yahoo ticker."""

        symbol = symbol.strip().upper()

        if symbol.endswith(".NS") or symbol.endswith(".BO"):
            return symbol

        if symbol.startswith("^"):
            return symbol

        return f"{symbol}.NS"

    @staticmethod
    def _find_column(
        dataframe: pd.DataFrame,
        candidates: tuple[str, ...],
        required: bool = True,
    ) -> str | None:
        """Find the first matching column from candidates."""

        for candidate in candidates:
            if candidate in dataframe.columns:
                return candidate

        if required:
            raise ValueError(f"Missing required column. Expected one of: {candidates}")

        return None
